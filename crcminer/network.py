import os
import logging
import argparse
import networkx as nx
import pandas as pd


SCRIPT_PATH = os.path.abspath(__file__)
FORMAT = "[%(asctime)s] %(levelname)s %(message)s"
l = logging.getLogger()
lh = logging.StreamHandler()
lh.setFormatter(logging.Formatter(FORMAT))
l.addHandler(lh)
l.setLevel(logging.INFO)
debug = l.debug
info = l.info
warning = l.warning
error = l.error


def parse_bed(_infile):
    """
    input: motif bed file
      chr	st	en	gene	motif
    chr1	10	20	A,B,C	BAR
    chr1	11	21	FOO	X,Y,Z
    chr1	1111	1121	JANE1	DOE
    chr1	11131	11421		FOO1
    chr1	11151	11521	BAR1
    output:
    edgelist: [['A', 'BAR'], ['B', 'BAR'], ['C', 'BAR'], ['FOO', 'X'], ['FOO', 'Y'], ['FOO', 'Z'], ['JANE1', 'DOE']]

    """
    df = pd.read_csv(_infile, sep="\t")
    df = df[["gene", "motif"]]  # these names are mocked.
    df2 = df.dropna()
    df2 = (
        df2.assign(gene=df2["gene"].str.split(","), motif=df2["motif"].str.split(","))
        .explode("gene")
        .explode("motif")
        .reset_index(drop=True)
    )
    # print(df.head())
    _list = df2.values.tolist()  # edgelist

    return _list


def networkX_helpers(input_nodelist):
    """
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
    text file with indegree, outdegree counts and CRC TF clique fractions.

    """
    # Create a networkx graph object
    info("Initializing Graph")
    _graph = nx.DiGraph()

    # Add edges to to the graph object
    info("Add edges to graph object")
    _graph.add_edges_from(input_nodelist)

    info("Calculating in-degree out-degree stats")

    # degrees_dict = {node:deg for (node, deg) in _graph.degree()}
    out_degree_dict = {node: deg for (node, deg) in _graph.out_degree()}
    in_degree_dict = {node: deg for (node, deg) in _graph.in_degree()}

    out_degree = pd.DataFrame(
        data={"TF": out_degree_dict.keys(), "Out": out_degree_dict.values()}
    )
    in_degree = pd.DataFrame(
        data={"TF": in_degree_dict.keys(), "In": in_degree_dict.values()}
    )

    NetworkMetricsOutput = pd.merge(
        out_degree, in_degree, left_on="TF", right_on="TF", how="outer"
    )
    # TOTAL DEGREE
    NetworkMetricsOutput["Total"] = (
        NetworkMetricsOutput["Out"] + NetworkMetricsOutput["In"]
    )

    info("Fetching self Loops")
    # Self loops
    # autoregulatoryLoops = nx.selfloop_edges(_graph) # not needed?

    selfLoops = list(nx.nodes_with_selfloops(_graph))

    info("Fetch selfregulatory loops")
    from itertools import product

    nodePairs = []
    for ele in list(product(selfLoops, repeat=2)):
        if (
            ele[0] != ele[1]
            and _graph.has_edge(ele[0], ele[1])
            and _graph.has_edge(ele[1], ele[0])
        ):
            nodePairs.append(ele)

    info("Fetch Self regulating Clique")
    unDirGraph = nx.from_edgelist(nodePairs)
    cliqueGen = nx.find_cliques_recursive(unDirGraph)
    cliqueList = list(cliqueGen)

    # I am not sure what this does at this point but
    # this is a place holder until SV confirms
    # All cliques - not needed right now (SV)
    # cliqueGen_ALL = list(nx.find_cliques_recursive(_graph))

    print("hi", len(cliqueList))
    info("Scores all the CRC's")
    """
  ## SCORING THE CRCs using sum outdegree for each TF and dividing by the number of TFs in the clique
  """
    cliqueRanking = []
    outDegreeDict = _graph.out_degree()

    for crcs in cliqueList:
        score = 0
        for gene in crcs:
            score += outDegreeDict[gene]
        score = score / len(crcs)
        if score > 0 and len(crcs) > 2:
            cliqueRanking.append((crcs, score))

    sortedRankedCliques = pd.DataFrame(
        sorted(cliqueRanking, reverse=True, key=lambda x: x[1])
    )

    factorEnrichmentDict = dict.fromkeys(selfLoops, 0)

    info("Calculate enrichment of each TF in a CRC clique")
    """
  ## Enrichment of each TF calculated as (number of CRC cliques with the given TF)/(number of CRC cliques)
  """
    for crcClique in cliqueList:
        for TF in crcClique:
            factorEnrichmentDict[TF] += 1

    factorRankingTable = dict.fromkeys(selfLoops, 0)
    for TF in selfLoops:
        factorRankingTable[TF] = factorEnrichmentDict[TF] / float(len(cliqueRanking))

    FactorRank = pd.DataFrame(
        data={
            "TF": factorRankingTable.keys(),
            "TF_CliqueFraction": factorRankingTable.values(),
        }
    )

    TFSpecificCliques = nx.cliques_containing_node(unDirGraph)

    NetworkMetricsOutput = pd.merge(
        NetworkMetricsOutput, FactorRank, left_on="TF", right_on="TF", how="outer"
    )

    info("Write to file")
    NetworkMetricsOutput.to_csv("TF_Degrees.csv", index=False)
    sortedRankedCliques.to_csv("Putative_CRC_Cliques.csv", index=False, header=False)

    # print(nx.cliques_containing_node(unDirGraph,"RFX3"))
    # print(len(nx.cliques_containing_node(unDirGraph,"RFX3")))
    # print(TFSpecificCliques)

    return _graph


DESCRIPTION = """
Create networkx objects. 
"""


EPILOG = """
"""


class CustomFormatter(
    argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter
):
    pass


parser = argparse.ArgumentParser(
    description=DESCRIPTION, epilog=EPILOG, formatter_class=CustomFormatter
)

parser.add_argument("arg")
parser.add_argument(
    "-v", "--verbose", action="store_true", help="Set logging level to DEBUG"
)

args = parser.parse_args()

edge_list = parse_bed(args.arg)
networkX_helpers(edge_list)


if args.verbose:
    l.setLevel(logging.DEBUG)

debug("%s begin", SCRIPT_PATH)
