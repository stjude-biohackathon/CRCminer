#!/usr/bin/env python3

import mygene

mg = mygene.MyGeneInfo()

motif_lines = []
genes = []
motifs_dict = {}

with open("homo_sapiens.meme", "r") as file:
    for line in file:
        if line.startswith("MOTIF"):
            motif_lines.append(line)

# TODO - This whole script should be made into a function that takes a regex for extracting the
# query ID from the motif name.
# This would allow it to be generalized to the other name formats from the other motif databases more easily.
for line in motif_lines:
    words = line.split()
    if len(words) >= 3:
        gene = words[2]
        if gene.startswith("("):
            start = gene.find("(")  # find the start index of the first opening bracket
            end = gene.find(")")  # # find the end index of the first closing bracket
            if start != -1 and end != -1:  # if there is at least one pair of brackets
                substring = gene[start + 1 : end]  # extract the substring between the brackets
                gene = substring.split("_")[0]  # extract the first string before the first underscore
        motifs_dict[words[1]] = gene  # motifs_dict['M00234_2.00'] = 'OVOL2'
        genes.append(gene)

geneAnns = mg.querymany(
    genes, scopes="symbol", fields="entrezgene,symbol,ensembl.gene", species="human"
)


with open("Homo_sapiens.id_map.csv", "w") as out:
    for ann in geneAnns:
        query = ann["query"]
        motif = list(filter(lambda x: motifs_dict[x] == query, motifs_dict))[0]

        if "notfound" in ann:
            print(f"{motif},{query},notfound,notfound,notfound", file=out)
            continue

        if query != ann["symbol"]:
            print(f"{motif},{query},badmatch,badmatch,badmatch", file=out)
            continue

        symbol = ann["symbol"]

        # check if ensembl key is available
        try:
            e = ann["ensembl"]
        except KeyError:
            # if no ensembl key
            e = None

        # if ensembl data found
        if e is not None:
            # check if ann['ensembl']['gene'] value is an array
            if e.__class__() == []:
                # if array
                # walk over the array items and collect ens gene ids and concat
                ensemblId = ";".join([i["gene"] for i in e])
            else:
                # if not array
                ensemblId = e["gene"]
        else:
            ensemblId = "notfound"

        try:
            entrezId = ann["entrezgene"]
        except KeyError:
            entrezId = "notfound"

        print(f"{motif},{query},{symbol},{entrezId},{ensemblId}", file=out)
