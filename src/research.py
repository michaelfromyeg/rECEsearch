'''
Collect research data using scholarly; see the README for more!
'''

from scholarly import scholarly
from typing import List, NamedTuple
import sys, getopt
import csv
import shelve

# Data definitions

class Data(NamedTuple):
  lab: str
  lab_id: str
  url: str

class Publication(NamedTuple):
  title: str
  authors: str
  year: int
  citations: int
  publisher: str

class Research(NamedTuple):
  lab: str
  lab_id: str
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

debug = True

# Functions

def main(filenames: [str, str]) -> None:
  '''
  Read data, analyze it, and output it
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
    with open (f'../data/{filename}') as csv_file:

      # Setup CSV reader
      csv_reader = csv.reader(csv_file, delimiter=',')
      line_count = 0
      
      # Loop through file
      for row in csv_reader:
          # Parse headers
          if line_count == 0:
              print(f'{bcolors.WARNING}Column names are {", ".join(row)}. You should have Lab, ID, URL (in that order); if you do not, please consult the README.md.{bcolors.ENDC}')
              line_count += 1
          # Append row to lod
          else:
              if (debug):
                print(f'{bcolors.OKBLUE}Lab: {row[0]}\tID: {row[1]}\tURL: {row[2]}{bcolors.ENDC}')
              d = Data(row[0], row[1], row[2])
              lod.append(d)
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
      print(f'Trying {d.lab}...')

    lab = None
    if (debug):
      data = shelve.open('data')
      lab = data['biot']
    else:
      lab = scholarly.search_author_id(id=d.lab_id, fill=True)
      
    # Compile all publications
    lop = [] # List[Publication]
    # p's type is given by scholarly
    for p in lab.publications[:2]:
      p.fill()
      bib = p.bib
      custom_pub = Publication(bib['title'], bib['author'], int(bib['year']), get_citations(p.cites_per_year), bib['publisher'])
      lop.append(custom_pub)
    
    # Attach professor to publications
    r = Research(d.lab, d.lab_id, lop)
    lor.append(r)
  print(f'{bcolors.OKGREEN}Done gathering research! Now creating the output file...{bcolors.ENDC}')
  return lor

def generate(lod: List[Data], output_file: str) -> None:
  '''
  Generate csv file from given research
  '''
  # Get research from data
  lor = research(lod)

  # Write list of research data to a csv file
  with open(f'../output/{output_file}', 'w', newline='') as o:
    writer = csv.writer(o)
    writer.writerow(['Lab', 'Lab ID', 'Publications', 'Title', 'Author', 'Year', 'Cited By', 'Publisher'])
    r: Research
    for r in lor:
      writer.writerow([r.lab, r.lab_id, '...'])
      p: Publication
      for p in r.publications:
        writer.writerow(['', '', '', p.title, format_authors(p.authors), p.year, p.citations, p.publisher])
  print(f'{bcolors.OKGREEN}Done! Go check out: output/{output_file}.{bcolors.ENDC}')
  return None

def get_citations(cites_per_year: dict) -> int:
  '''
  Helper function to process cites per year to a single number
  '''
  return sum(cites_per_year.values())

def format_authors(authors: str) -> str:
  '''
  Helper function to *cleanly* format authors
  '''
  if (len(authors) > 20):
    return authors[:20]
  return authors

def get_args(argv: List[str]) -> [str, str]:
  input_file = ''
  output_file = ''
  try:
    opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
  except getopt.GetoptError:
    print('python research.py -i <inputfile> -o <outputfile>')
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
      print('python research.py -i <inputfile> -o <outputfile>')
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
  print(f'{bcolors.ENDC}') # just in case!