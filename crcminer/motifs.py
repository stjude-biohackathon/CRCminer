import pyfaidx
import pyranges
import pandas as pd
from pymemesuite.common import Alphabet, Background, Sequence, MotifFile
import Bio.SeqIO
from pymemesuite.fimo import FIMO

def extract_sequences_from_bed(fasta_path, bed_path, output_path):
    """Extract sequences from a FASTA file based on a BED file of regions. Writes the sequences to an output file.

    :param fasta_path: Path to the genome FASTA file.
    :type fasta_path: str
    :param bed_path: Path to the BED file.
    :type bed_path: str
    :param output_path: Path to the output file.
    """
        
    
    # Open the FASTA file
    fasta = pyfaidx.Fasta(fasta_path)

    # Open the output file
    with open(output_path, 'w') as output_file:
        # Open the BED file
        with open(bed_path, 'r') as bed_file:
            for line in bed_file:
                fields = line.strip().split('\t')
                chrom = fields[0]
                start = int(fields[1])
                end = int(fields[2])
                # Use pyfaidx to extract the sequence
                sequence = fasta[chrom][start:end]
                # Write the sequence to the output file
                output_file.write(f'>{chrom}:{start}-{end}\n')
                output_file.write(str(sequence) + '\n')
                

def intersect_beds(bed1, bed2, output_bed):
    '''Intersect bed1 ranges with bed2 ranges and output overlapping bed1 ranges to a new BED file.

    :param bed1: Path to the first BED file.
    :type bed1: str
    :param bed2: Path to the second BED file.
    :type bed2: str
    :param output_bed: Path to the output BED file.
    :type output_bed: str
    '''
    
    bed2_df = pyranges.read_bed(bed2)
    bed1_df = pyranges.read_bed(bed1)
    result = bed1_df.intersect(bed2_df)
    
    result.to_csv(output_bed, sep='\t', header = False)


def get_background(fasta):
    '''
    Get the background nucleotide sequences from a FASTA file.
    
    :param fasta: Path to the FASTA file.
    :type fasta: str
    ...
    :return: Background nucleotide sequences as a pymemesuite Background object.
    :rtype: :class:`pymemesuite.common.Background` 
    '''
    
    alphabet = Alphabet.dna()
    
    # Read in all sequences from subpeak FASTA.
    sequences = [
        Sequence(str(record.seq), name=record.id.encode())
        for record in Bio.SeqIO.parse(fasta, "fasta")
    ]
    
    bg_seq = Background.from_sequences(alphabet, *sequences)
    return bg_seq
    

def filter_enhancers_to_active_genes(active_gene_file, enhancers_file, id_cols = ["OVERLAP_GENES", "PROXIMAL_GENES", "CLOSEST_GENE"]):
    '''
    Filter enhancer file to active gene associations.
    
    If enhancer has no associated gene in active gene list, it should be removed from output.
    If enhancer has non-active gene in associated gene list, that gene should be removed from the "active_genes" column.
    
    :param active_gene_file: Path to the file containing the list of active genes, one per line.
    :type active_gene_file: str
    :param enhancers_file: Path to the tab-delimited file containing the enhancers.
    :type enhancers_file: str
    :param id_cols: List of column names in the enhancers file that contain the gene IDs that should be concatenated and uniquified to form the "all_genes" column.
    :type id_cols: list
    ...
    :return: pandas dataframe of enhancers associated with active genes.
    :rtype: :class:`pandas.DataFrame`
    '''

    # Read in active genes.
    with open(active_gene_file) as f:
        active_genes = f.readlines()
    
    # Read enhancers.
    enh_df = pd.read_table(enhancers_file)
    
    # TODO - Test, this may not actually work. Definitely throws a warning if it does.

    # concatenate and uniquify values across columns
    enh_df["all_genes"] = enh_df[id_cols].astype(str).T.apply(lambda x: x.str.split(",")).apply(lambda x: ','.join(pd.Series(sum(x,[])).drop_duplicates()))

    enh_df = enh_df[enh_df["all_genes"].str.contains('|'.join(active_genes))].copy()

    enh_df["active_genes"] = enh_df["active_genes"].apply(lambda x: x.split(",")).apply(lambda x: ",".join([y for y in x if y in active_genes]))
        
    # pandas dataframe of enhancers associated with active genes
    return enh_df 


def scan_for_motifs(motif_file, fasta_file, fimo_background, output_file, id_map_col = "Symbol", 
                    motif_id_map = None, active_genes = None, threshold = 1e-4, occurence_cutoff = 1):
    '''
    
    :param motif_file: Path to the motif file.
    :type motif_file: str
    :param fasta_file: Path to the FASTA file.
    :type fasta_file: str
    :param fimo_background: Background nucleotide sequences as a pymemesuite Background object.
    :type fimo_background: :class:`pymemesuite.common.Background`
    :param output_file: Path to the output file.
    :type output_file: str
    :param id_map_col: Column name in the motif ID map file that contains the gene ID.
    :type id_map_col: str
    :param active_genes: List of active genes. If None, all genes are considered active and no filtering is performed.
    :type active_genes: list
    :param threshold: Threshold for FIMO p-value.
    :type threshold: float
    :param occurence_cutoff: Minimum number of motif occurences to count as an edge connection downstream.
    :type occurence_cutoff: int
    '''
    
    sequences = [
        Sequence(str(record.seq), name=record.id.encode())
        for record in Bio.SeqIO.parse(fasta_file, "fasta")
    ]

    fimo = FIMO(both_strands = True, threshold = threshold)
    
    # Read in motif mappings.
    if motif_id_map is not None:
        motif_mappings = pd.read_table(motif_id_map, header = True)
    
    # Iterate through motifs in PWM file and find instances.
    # TODO - Multiprocessing?
    with MotifFile(motif_file) as motif_file, open(output_file, 'w') as out:
        for motif in motif_file:
        
            # If active genes provided, check if PWM gene/ID matches any of the active genes.
            if active_genes is not None:
            
                motif_id = motif_id_map[motif.accession.decode()]
                if motif_id not in active_genes:
                    
            
            
    
            pattern = fimo.score_motif(motif, sequences, fimo_background)

            # TODO - Implement occurence_cutoff filtering. If > 1, need to collapse overlapping matched elements and count them as one.
            # Then only need to report the match if the number of occurences is >= occurence_cutoff.
            
            for m in pattern.matched_elements:
                print(
                    m.source.accession.decode(),
                    m.start,
                    m.stop,
                    m.strand,
                    m.score,
                    m.pvalue,
                    m.qvalue,
                    file = out,
                    sep = "\t"
                )
    
    
