import os
import logging
import argparse
import networkx as nx
import pandas as pd


SCRIPT_PATH = os.path.abspath(__file__)
FORMAT = '[%(asctime)s] %(levelname)s %(message)s'
l = logging.getLogger()
lh = logging.StreamHandler()
lh.setFormatter(logging.Formatter(FORMAT))
l.addHandler(lh)
l.setLevel(logging.INFO)
debug = l.debug; info = l.info; warning = l.warning; error = l.error



def parse_bed(_infile):
    '''
    input: motif bed file 
      chr	st	en	gene	motif
    chr1	10	20	A,B,C	BAR
    chr1	11	21	FOO	X,Y,Z
    chr1	1111	1121	JANE1	DOE
    chr1	11131	11421		FOO1
    chr1	11151	11521	BAR1
    output:
    edgelist: [['A', 'BAR'], ['B', 'BAR'], ['C', 'BAR'], ['FOO', 'X'], ['FOO', 'Y'], ['FOO', 'Z'], ['JANE1', 'DOE']]

    '''
    df = pd.read_csv(_infile, sep='\t')
    df = df[['gene','motif']] # these names are mocked. 
    df2=df.dropna()
    df2=df2.assign(gene=df2['gene'].str.split(','), 
    motif=df2['motif'].str.split(',')).explode('gene').explode('motif').reset_index(drop=True)
    # print(df.head())
    _list=df2.values.tolist() # edgelist
    
    return _list


def networkX_helpers(input_TFbed):
  '''
  Input is a node edge list
  These will have both node and edge list 
  my_graph.add_edges_from([('A', 'B'), 
                            ('A', 'D'), 
                            ('A', 'E'), 
                            ('A', 'G'), 
                            ('A', 'H'), 
                            ('B', 'C'), 
                            ('B', 'E'), 
                            ('C', 'I'), 
                            ('C', 'K'), 
                            ('C', 'L'), 
                            ('D', 'A'), 
                            ('D', 'C'), 
                            ('D', 'H'), 
                            ('D', 'I'), 
                            ('A', 'A'),('H','H'),('D','D'),('H','A'),('H','D')])
  Output: 
  text file with indegree and outdegree counts. 

  '''

  # Create a networkx graph object
  info("Initializing Graph")
  _graph = nx.DiGraph() 

  # Add edges to to the graph object
  info("Add edges to graph object")
  _graph.add_edges_from(edge_list)

  info("Calculating indegree outdegree stats")
  InDegreeDict = _graph.in_degree()
  OutDegreeDict = _graph.out_degree()

  # writing this out to a file


  info("Fetching self Loops")
  # Self loops
  autoregulatoryLoops = nx.selfloop_edges(_graph) # not needed?

  selfLoops = list(nx.nodes_with_selfloops(_graph))

  info("Fetch selfregulatory loops")
  from itertools import product
  pairs=[]
  for ele in list(product(selfLoops,repeat=2)):
      if ele[0] == ele[1]:
        continue
      pairs.append(ele)

  info("Fetch Clique")
  unDirGraph = nx.from_edgelist(pairs)
  cliqueGen = nx.find_cliques_recursive(unDirGraph)
  cliqueList = list(cliqueGen)

  # I am not sure what this does at this point but
  # this is a place holder until SV confirms
  cliqueGen_ALL = list(nx.find_cliques_recursive(_graph))

  info("Scores all the CRC's")
  '''
  ## SCORING THE CRCs using sum outdegree for each TF and dividing by the number of TFs in the clique
  '''
  cliqueRanking = []
  outDegreeDict = my_graph.out_degree()

  for crcs in cliqueList:
      score = 0
      for gene in crcs:
          score += outDegreeDict[gene]
      score = score/len(crcs)
      if score > 0 and len(crcs) > 2:
          cliqueRanking.append((crcs, score))
              
              
  sortCliqueRanking = sorted(cliqueRanking, reverse=True, key=lambda x:x[1])
  
  return  sortCliqueRanking # may be write this to table?


DESCRIPTION = '''
Create networkx objects. 
'''



EPILOG = '''
'''

class CustomFormatter(argparse.ArgumentDefaultsHelpFormatter,
    argparse.RawDescriptionHelpFormatter):
  pass
parser = argparse.ArgumentParser(description=DESCRIPTION, epilog=EPILOG,
  formatter_class=CustomFormatter)

parser.add_argument('arg')
parser.add_argument('-v', '--verbose', action='store_true',
    help='Set logging level to DEBUG')

args = parser.parse_args()

edge_list = parse_bed(args.arg)
networkX_helpers(edge_list)


if args.verbose:
  l.setLevel(logging.DEBUG)

debug('%s begin', SCRIPT_PATH)

