
import os
import logging
import argparse

SCRIPT_PATH = os.path.abspath(__file__)
FORMAT = '[%(asctime)s] %(levelname)s %(message)s'
l = logging.getLogger()
lh = logging.StreamHandler()
lh.setFormatter(logging.Formatter(FORMAT))
l.addHandler(lh)
l.setLevel(logging.INFO)
debug = l.debug; info = l.info; warning = l.warning; error = l.error

def parse_bed(_infile):
     import pandas as pd
     df = pd.read_csv(_infile, sep='\t')
     df = df[['gene','motif']] # these names are mocked. 
     df2=df.dropna()
     df2=df2.assign(gene=df2['gene'].str.split(','), 
     motif=df2['motif'].str.split(',')).explode('gene').explode('motif').reset_index(drop=True)
     # print(df.head())
     _list=df2.values.tolist() # edgelist
     # return tuple
     # (['A', 'BAR'], ['B', 'BAR'], ['C', 'BAR'], ['FOO', 'X'], ['FOO', 'Y'], ['FOO', 'Z'], ['JANE1', 'DOE'])
     return list(df2.itertuples(index=False, name=None))




def network_jaccard(edgelist1, edgelist2):
  '''
  inputs:
  edgelist1: output from parse_bed for sampleX

  edgelist2: output from parse_bed for sampleY

  Output: 
  float: indicating similarity index

  ref:
  https://medium.com/rapids-ai/similarity-in-graphs-jaccard-versus-the-overlap-coefficient-610e083b877d

  '''

  edgeintersection = len(set(edgelist1).intersection(edgelist2))
  edgeunion = (len(edgelist1) + len(edgelist2)) - edgeintersection

  print(float((edgeintersection) / edgeunion))
  return float((edgeintersection) / edgeunion)

DESCRIPTION = '''
When you have two different network graph
objects between mutiple samples 
compare them using jaccard similarity index
'''

EPILOG = '''
'''

class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter,
    argparse.RawDescriptionHelpFormatter):
  pass
parser = argparse.ArgumentParser(description=DESCRIPTION, epilog=EPILOG,
  formatter_class=CustomFormatter)

parser.add_argument('edgelist1')
parser.add_argument('-v', '--verbose', action='store_true',
    help='Set logging level to DEBUG')

args = parser.parse_args()

e1 = parse_bed(args.edgelist1)
# print e1
# [('A', 'BAR'), ('B', 'BAR'), ('C', 'BAR'), ('FOO', 'X'), ('FOO', 'Y'), ('FOO', 'Z'), ('JANE1', 'DOE')]
# copying the same set for testing. 
e2 = parse_bed(args.edgelist1)
e2 = e2[0:3] # subsetting 
# print(e2)
# [('A', 'BAR'), ('B', 'BAR'), ('C', 'BAR')]

network_jaccard(e1, e2) # should print out  0.42857142857142855

if args.verbose:
  l.setLevel(logging.DEBUG)

debug('%s begin', SCRIPT_PATH)

