"""
Collect research data using scholarly; see the README for more!
"""

from typing import List, NamedTuple
from enum import Enum
import sys
import getopt
import csv
import shelve
from scholarly import scholarly

# Data definitions


class Data(NamedTuple):
    """
    Data as read in from a spreadsheet
    """

    lab: str
    lab_id: str
    url: str


class Publication(NamedTuple):
    """
    Structured publication data gathered from scholarly
    """

    title: str
    authors: str
    year: int
    citations: int
    publisher: str


class Research(NamedTuple):
    """
    Structured research data gathered from scholarly
    """

    lab: str
    lab_id: str
    publications: List[Publication]


class TerminalColors(Enum):
    """
    Terminal colors for fancy printing
    """

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


DEBUG = False

# Functions


def main(filenames: [str, str]) -> None:
    """
    Read data, analyze it, and output it
    """
    if DEBUG:
        print("Starting in debug mode...")
    input_file = filenames[0]
    output_file = filenames[1]
    generate(read(input_file), output_file)


def read(filename: str) -> List[Data]:
    """
    Read in file data from given csv
    """

    # List of csv data
    lod = []  # type: List[Data]

    try:
        with open(f"../data/{filename}") as csv_file:

            # Setup CSV reader
            csv_reader = csv.reader(csv_file, delimiter=",")
            line_count = 0

            # Loop through file
            for row in csv_reader:
                # Parse headers
                if line_count == 0:
                    print(
                        f"""{TerminalColors.WARNING}Column names are {", ".join(row)}.
                        You should have Lab, ID, URL (in that order);
                        if you do not, please consult the README.md.{TerminalColors.ENDC}"""
                    )
                    line_count += 1
                # Append row to lod
                else:
                    if DEBUG:
                        print(
                            f"""{TerminalColors.OKBLUE}Lab: {row[0]}\t
                            ID: {row[1]}\t
                            URL: {row[2]}{TerminalColors.ENDC}"""
                        )
                    data = Data(row[0], row[1], row[2])
                    lod.append(data)
                    line_count += 1
            print(
                f"""{TerminalColors.OKGREEN}Processed {line_count} lines...
                now gathering research!{TerminalColors.ENDC}"""
            )

    # Catch bad -i value
    except FileNotFoundError:
        print(
            f"""{TerminalColors.FAIL}Hmm... that file wasn't found.
             Make sure {filename} exists in the data folder.{TerminalColors.ENDC}"""
        )
        return None

    return lod


def get_research(lod: List[Data]) -> List[Research]:
    """
    Takes list of professor data, hands it to scholarly, returns list of research data
    """

    # List of professors with their attached research
    lor = []  # List[Research]

    data: Data
    for data in lod:
        if DEBUG:
            print(f"Trying {data.lab}...")

        lab = None
        if DEBUG:
            # Don't make extra API calls (worried about 429), instead load in "shelved" data
            # If you don't have any data shelved, add the else case here one once;
            # you could also run p.fill() on the pubs if you want to save
            # filled data
            data = shelve.open("data")
            lab = data["biot"]
        else:
            lab = scholarly.search_author_id(data.lab_id)
            try:
                lab.fill()
            except AttributeError:
                continue

        # Compile all publications
        lop = []  # List[Publication]

        count = 0

        # p's type is given by scholarly
        for publication in lab.publications:
            # Only collect 50 publications max per lab
            if count > 10:
                break
            try:
                publication.fill()
                bib = publication.bib
                custom_pub = None
                try:
                    custom_pub = Publication(
                        bib["title"],
                        bib["author"],
                        int(bib["year"]),
                        get_citations(publication.cites_per_year),
                        bib["publisher"],
                    )
                except KeyError:
                    custom_pub = Publication(
                        bib["title"],
                        "n/a",
                        int(bib["year"]),
                        get_citations(publication.cites_per_year),
                        "n/a",
                    )
                    print(bib["title"] + " was missing information")
                lop.append(custom_pub)
                count += 1
            except Exception:
                continue

        # Attach professor to (sorted) publications
        research = Research(data.lab, data.lab_id, lop)
        lor.append(research)
    print(
        f"""{TerminalColors.OKGREEN}Done gathering research!
         Now creating the output file...{TerminalColors.ENDC}"""
    )
    return lor


def generate(lod: List[Data], output_file: str) -> None:
    """
    Generate csv file from given research
    """
    # Get research from data
    lor = get_research(lod)

    # Write list of research data to a csv file
    with open(f"../output/{output_file}", "w", newline="") as output:
        writer = csv.writer(output)
        writer.writerow(
            [
                "Lab",
                "Lab ID",
                "Publications",
                "Title",
                "Author",
                "Year",
                "Cited By",
                "Publisher",
            ]
        )
        research: Research
        for research in lor:
            writer.writerow(
                [research.lab, research.lab_id, "...", "", "", "", "", "",]
            )
            publication: Publication
            for publication in research.publications:
                writer.writerow(
                    [
                        "",
                        "",
                        "",
                        publication.title,
                        format_authors(publication.authors),
                        publication.year,
                        publication.citations,
                        publication.publisher,
                    ]
                )
    print(
        f"{TerminalColors.OKGREEN}Done! Go check out: output/{output_file}.{TerminalColors.ENDC}"
    )


def get_citations(cites_per_year: dict) -> int:
    """
    Helper function to process cites per year to a single number
    """
    return sum(cites_per_year.values())


def format_authors(authors: str) -> str:
    """
    Helper function to *cleanly* format authors
    """
    if len(authors) > 20:
        return authors[:100] + "..."
    return authors


def get_args(argv: List[str]) -> [str, str]:
    """
    Get command line arguments (file names), return both in form [input file, output file]
    """
    input_file = ""
    output_file = ""
    try:
        opts, _ = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print("python research.py -i <inputfile> -o <outputfile>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print("python research.py -i <inputfile> -o <outputfile>")
            sys.exit()
        elif opt in ("-i", "--input"):
            input_file = arg
        elif opt in ("-o", "--output"):
            output_file = arg
    if DEBUG:
        print("Input file:", input_file)
        print("Output file:", output_file)
    return [input_file, output_file]


if __name__ == "__main__":
    main(get_args(sys.argv[1:]))
    print(f"{TerminalColors.ENDC}")  # just in case!
