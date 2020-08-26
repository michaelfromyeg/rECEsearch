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


class ExcelData(NamedTuple):
    """
    Data as read in from a spreadsheet
    """

    lab: str
    lab_id: str
    url: str


class PublicationData(NamedTuple):
    """
    Structured publication data gathered from scholarly
    """

    title: str
    authors: str
    year: int
    citations: int
    publisher: str


class ResearchData(NamedTuple):
    """
    Structured research data gathered from scholarly
    """

    lab: str
    lab_id: str
    publications: List[PublicationData]


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


DEBUG = True


class Research:
    def __init__(self, filenames: [str, str]):
        self.input_file = filenames[0]
        self.output_file = filenames[1]

    def main(self) -> None:
        """
        Read data, analyze it, and output it
        """
        if DEBUG:
            print("Starting in debug mode...")
        self.generate(self.read(self.input_file), self.output_file)
    
    def research_for_groups(self) -> List[ResearchData]:
        return self.get_research(self.read(self.input_file))

    def read(self, filename: str) -> List[ExcelData]:
        """
        Read in file data from given csv
        """

        # List of csv data
        lod = []  # type: List[ExcelData]

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
                            f"""{TerminalColors.WARNING.value}Column names are {", ".join(row)}. You should have Lab, ID, URL (in that order); if you do not, please consult the README.md.{TerminalColors.ENDC.value}"""
                        )
                        line_count += 1
                    # Append row to lod
                    else:
                        if DEBUG:
                            print(
                                f"""{TerminalColors.OKBLUE.value}Lab: {row[0]}\tID: {row[1]}\tURL: {row[2]}{TerminalColors.ENDC.value}"""
                            )
                        data = ExcelData(row[0], row[1], row[2])
                        lod.append(data)
                        line_count += 1
                print(
                    f"""{TerminalColors.OKGREEN.value}Processed {line_count} lines...now gathering research!{TerminalColors.ENDC.value}"""
                )

        # Catch bad -i value
        except FileNotFoundError:
            print(
                f"""{TerminalColors.FAIL.value}Hmm... that file wasn't found.
                Make sure {filename} exists in the data folder.{TerminalColors.ENDC.value}"""
            )
            return None

        return lod

    def get_research(self, lod: List[ExcelData]) -> List[ResearchData]:
        """
        Takes list of professor data, hands it to scholarly, returns list of research data
        """

        # List of professors with their attached research
        lor = []  # List[Research]

        data: ExcelData
        for data in lod:
            if DEBUG:
                print(f"Trying {data.lab}...")

            lab = None
            if DEBUG and False:
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
                    print(f"Lab came out as {lab}, which wasn't fillable!")
                    continue

            # Compile all publications
            lop = []  # List[Publication]

            count = 0
            # p's type is given by scholarly
            max: int
            if DEBUG:
                max = 9
            else:
                max = 50
            for publication in lab.publications:
                added = False
                # Only collect 50 publications max per lab
                if count > max:
                    break
                try:
                    publication.fill()
                    bib = publication.bib
                    custom_pub = None
                    try:
                        custom_pub = PublicationData(
                            bib["title"],
                            bib["author"],
                            int(bib["year"]),
                            self.get_citations(publication.cites_per_year),
                            bib["publisher"],
                        )
                        added = True
                    except KeyError:
                        continue
                        # custom_pub = PublicationData(
                        #     bib["title"],
                        #     "n/a",
                        #     int(bib["year"]),
                        #     self.get_citations(publication.cites_per_year),
                        #     "n/a",
                        # )
                        # print(bib["title"] + " was missing information")
                    if custom_pub is not None:
                        lop.append(custom_pub)
                    if added:
                        count += 1
                except Exception:
                    continue

            # Attach professor to (sorted) publications
            research = ResearchData(data.lab, data.lab_id, lop)
            lor.append(research)
        print(
            f"""{TerminalColors.OKGREEN.value}Done gathering research! Now creating the output file...{TerminalColors.ENDC.value}"""
        )
        return lor

    def generate(self, lod: List[ExcelData], output_file: str) -> None:
        """
        Generate csv file from given research
        """
        # Get research from data
        lor = self.get_research(lod)

        # Write list of research data to a csv file
        with open(
            f"../output/{output_file}", "w", newline="", encoding="utf-8"
        ) as output:
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
            research: ResearchData
            for research in lor:
                writer.writerow(
                    [research.lab, research.lab_id, "...", "", "", "", "", "",]
                )
                publication: PublicationData
                for publication in research.publications:
                    writer.writerow(
                        [
                            "",
                            "",
                            "",
                            publication.title,
                            self.format_authors(publication.authors),
                            publication.year,
                            publication.citations,
                            publication.publisher,
                        ]
                    )
        print(
            f"""{TerminalColors.OKGREEN.value}Done creating output file!{TerminalColors.ENDC.value}"""
        )

    def get_citations(self, cites_per_year: dict) -> int:
        """
        Helper function to process cites per year to a single number
        """
        return sum(cites_per_year.values())

    def format_authors(self, authors: str) -> str:
        """
        Helper function to *cleanly* format authors
        """
        # TODO: figure out a better way to implement this... don't want to remove contributors
        # if len(authors) > 20:
        #     return authors[:100] + "..."
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
    research = Research(filenames=get_args(sys.argv[1:]))
    research.main()
    print(f"{TerminalColors.ENDC.value}")  # just in case!
