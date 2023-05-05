# CRCminer
Transcription factors are responsible for controlling the activation and deactivation of genes and usually work together in combinations. Researchers studying embryonic stem cells and other types of cells have discovered a group of transcription factors that regulate cell identity and state. These key transcription factors create interconnected loops that reinforce the specific gene-expression program unique to each cell type. This collection of core transcription factors and their regulatory loops is known as the core transcriptional regulatory circuitry. CRCminer takes advantage of the fact that a vast majority of prominent master transcription factors are governed by super enhancers and that they control the enhancers of other master transcription factors. Upon receiving a set of super enhancers and a catalog of active genes as input, CRC analysis goes on to meticulously compute the IN and OUT degrees of each transcription factor. IN degree quantifies the number of unique transcription factors that regulate the given gene, whereas OUT degree denotes the count of other transcription factors regulated by the same transcription factor. This intricate and sophisticated approach provides an in-depth and nuanced comprehension of the core transcriptional regulatory circuitry, enabling researchers to unravel its mysteries with precision and accuracy.

![image](https://user-images.githubusercontent.com/107953299/236574166-e05eb6db-fa48-4730-999d-8bc26265a523.png)

Source: https://github.com/linlabcode/CRC



## Dependencies 

* Python
* Pymemesuite
* Pyfaidx 
* Biopython
* Networkx
* Pyranges 
* Pandas
* Sphinx
* Dash
* Cytoscape
* Plotly

## Install

```
pip install crcminer
```

## Usage

As a command line tool

```
python crcminer.py report [commands] 
```

Commands:  
`compare`  - Compare two networks  
`mine` - Mines for CRC  
`report` - report vizualization

`compare` command options :  

Compare two networks



`mine` command options :     

mines for CRC

`--fasta PATH ` - fasta   
`--enhancer PATH` - ROSE2 output of annotated (super)enhancer  
`--mapping PATH` - Motif ID to gene ID mapping file   
`--help` - Show this message and exit  
