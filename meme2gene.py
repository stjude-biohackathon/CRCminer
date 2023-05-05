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


for line in motif_lines:
    words = line.split()
    if len(words) >= 3:
        gene = words[2]
        if gene.startswith("("):
            start = gene.find("(") # find the start index of the first opening bracket
            end = gene.find(")")   # # find the end index of the first closing bracket
            if start != -1 and end != -1:  # if there is at least one pair of brackets
                substring = gene[start+1:end] # extract the substring between the brackets
                gene = substring.split("_")[0] ## extract the first string before the first underscore
        motifs_dict[words[1]] = gene # motifs_dict['M00234_2.00'] = 'OVOL2'
        genes.append(gene)

geneAnns= mg.querymany(genes, scopes='symbol', fields='entrezgene,symbol,ensembl.gene', species='human')


key = "ensembl"
exception_count = 0
for ann in geneAnns:
    # check if ensembl key is available
    nf = False
    try:
        e = ann['ensembl']
    except KeyError:
        # if no ensembl key 
        nf = True

    # if ensembl data found
    if not nf:
        # check if ann['ensembl']['gene'] value is an array
        if e.__class__() == []: 
            # if array
            # walk over the array items and collect ens gene ids and concat
            ensemblId = ';'.join( [i['gene'] for i in e] )
        else:
            # if not array
            ensemblId = e['gene']
        
        symbol = ann['symbol']
        
        try:
            entrezId = ann['entrezgene']
        except KeyError:
            entrezId = "notfound"
            
        # find the motif based on symbol 
        motif = list( filter(lambda x: motifs_dict[x] == symbol, motifs_dict))[0]
        print(f"MOTIF {motif} {symbol}, {symbol}, {symbol}, {entrezId}, {ensemblId}")
    else:
        # if no ensembl data found
        print(f"MOTIF {motif} {symbol}, {symbol}, {symbol}, notfound, notfound")
        
 