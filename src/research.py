'''
Collect research data using scholarly
'''

from scholarly import scholarly
from typing import List, NamedTuple
import sys, getopt
import csv

# Data definitions

class Data(NamedTuple):
  course: str
  prof: str
  email: str

class Publication(NamedTuple):
  year: int
  abstract: str
  title: str
  authors: str
  url: str

class Research(NamedTuple):
  prof: str
  publications: List[Publication]

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

debug = False

# Functions

def main(filenames: [str, str]) -> None:
  '''
  Read data, anlyze it, and output it
  '''
  input_file = filenames[0]
  output_file = filenames[1]
  generate(read(input_file), output_file)
  return None

def read(filename: str) -> List[Data]:
  '''
  Read in file data from given csv
  '''

  # List of csv data
  lod = [] # type: List[Data]

  try:
    with open(f'../data/{filename}') as csv_file:

      # Setup CSV reader
      csv_reader = csv.reader(csv_file, delimiter=',')
      line_count = 0
      
      # Loop through file
      for row in csv_reader:
          # Parse headers
          if line_count == 0:
              print(f'{bcolors.WARNING}Column names are {", ".join(row)}. You should have Course, Name, Email (in that order); if you do not, please consult the README.md.{bcolors.ENDC}')
              line_count += 1
          # Append row to lod
          else:
              if (debug):
                print(f'{bcolors.OKBLUE}Course: {row[0]}\tProfessor: {row[1]}\tEmail: {row[2]}{bcolors.ENDC}')
              r = Data(row[0], row[1], row[2])
              lod.append(r)
              line_count += 1
      print(f'{bcolors.OKGREEN}Processed {line_count} lines... now gathering research!{bcolors.ENDC}')
  
  # Catch bad -i value
  except FileNotFoundError:
    print(f"{bcolors.FAIL}Hmm... that file wasn't found. Make sure {filename} exists in the data folder.{bcolors.ENDC}")
    return None

  return lod

def research(lod: List[Data]) -> List[Research]:
  '''
  Takes list of professor data, hands it to scholarly, returns list of research data
  '''

  # List of professors with their attached research
  lor = [] # List[Research]

  d: Data
  for d in lod:
    if (debug):
      print(f'Trying {d.prof}...')
    search_query = scholarly.search_author(d.prof)
    author = next(search_query).fill()
    
    # Compile all publications
    lop = [] # List[Publication]
    # p's type is given by scholarly
    for p in author.publications[:2]:
      p.fill()
      bib = p.bib
      custom_pub = Publication(int(bib['year']), bib['abstract'], bib['title'], bib['author'], bib['url'])
      lop.append(custom_pub)
    
    # Attach professor to publications
    r = Research({d.prof},lop)
    lor.append(r)
  return lor

def generate(lod: List[Data], output_file: str) -> None:
  '''
  Generate csv file from given research
  '''
  lor = research(lod)
  print(lor[0])
  return None

def get_args(argv: List[str]) -> [str, str]:
  input_file = ''
  output_file = ''
  try:
    opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
  except getopt.GetoptError:
    print('research.py -i <inputfile> -o <outputfile>')
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
      print('test.py -i <inputfile> -o <outputfile>')
      sys.exit()
    elif opt in ("-i", "--input"):
      input_file = arg
    elif opt in ("-o", "--output"):
      output_file = arg
  if (debug):
    print('Input file:', input_file)
    print('Output file:', output_file)
  return [input_file, output_file]

if __name__ == "__main__":
  main(get_args(sys.argv[1:]))
  print(f'{bcolors.ENDC}')