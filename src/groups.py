"""
Create research groups from CSV data
"""

from typing import List, NamedTuple
from enum import Enum
import sys
import getopt
import csv
import shelve
from research import Research, ResearchData, PublicationData

# Data definitions

class ExcelData(NamedTuple):
    """
    Data as read in from the groups spreadsheet
    """
    professor: str
    groups: str # Semi-colon separated values of given professor's research groups

class ProfessorData(NamedTuple):
    """
    """
    professor: str
    groups: List[str]

class GroupData(NamedTuple):
    """
    Formatted research data, by research group
    """
    name: str
    faculty: List[str]
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

class Group:
    def __init__(self, filenames: [str, str]):
        self.input_file = filenames[0]
        self.output_file = filenames[1]
    
    def main(self) -> None:
        """
        Read data, analyze it, and output it
        """
        if DEBUG:
            print("Starting in debug mode...")
        profs = self.covert_to_profs(self.read(self.input_file))
        research = self.get_research()
        result = self.group_research(profs, research)
        return None
    
    def read(self, filename: str) -> List[ExcelData]:
        """
        Read in file data from given csv
        """

        # List of csv data
        lod = [] # type: List[ExcelData]

        try:
            with open(f"../data/{filename}") as csv_file:
                
                # Setup csv reader
                csv_reader = csv.reader(csv_file, delimiter=",")
                line_count = 0

                # Loop through file
                for row in csv_reader:
                    # Parse headers
                    if line_count == 0:
                        print(
                            f"""{TerminalColors.WARNING.value}Column names are {", ".join(row)}. You should have Professor, Groups (in that order); if you do not, please consult the README.md.{TerminalColors.ENDC.value}"""
                        )
                        line_count += 1
                    # Append row to lod
                    else:
                        if DEBUG:
                            print(
                                f"""{TerminalColors.OKBLUE.value}Professor: {row[0]}\tGroups: {row[1]}{TerminalColors.ENDC.value}"""
                            )
                        data = ExcelData(row[0], row[1])
                        lod.append(data)
                        line_count += 1
                print(
                f"""{TerminalColors.OKGREEN.value}Processed {line_count} lines...now gathering research!{TerminalColors.ENDC.value}"""
                )
        except FileNotFoundError:
            print(
            f"""{TerminalColors.FAIL.value}Hmm... that file wasn't found.
            Make sure {filename} exists in the data folder.{TerminalColors.ENDC.value}"""
            )
            return None
        return lod
    
    def covert_to_profs(self, data: List[ExcelData]) -> List[ProfessorData]:
        lopd = [] # List[ProfessorData]
        for item in data:
            prof = ProfessorData(item.professor, item.groups.split(';'))
            lopd.append(prof)
        return lopd


    def get_research(self) -> List[ResearchData]:
        r = Research(["labs.csv", ""])
        lord = r.research_for_groups()
        return lord
    
    def group_research(self, research: List[ResearchData], professors: List[ProfessorData]) -> List[GroupData]:
        profs = [prof.name for prof in professors]
        groups = [prof.groups for prof in professors]
        prof_dict = dict(zip(profs, groups))
        print(prof_dict)
        return []

def get_args(argv: List[str]) -> [str, str]:
    """
    Get command line arguments (file names), return both in form [input file, output file]
    """
    input_file = ""
    output_file = ""
    try:
        opts, _ = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print("python groups.py -i <inputfile> -o <outputfile>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print("python groups.py -i <inputfile> -o <outputfile>")
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
    group = Group(filenames=get_args(sys.argv[1:]))
    group.main()
    print(f"{TerminalColors.ENDC.value}")  # just in case!