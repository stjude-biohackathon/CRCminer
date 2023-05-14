import rich_click as click


# Command Group
@click.group(name="CRCminer")
def CRCminer():
    """
    CRCminer: A tool for identifying CRCs from a set of (super)enhancers, with
    optional limitation to subpeaks (e.g. ATAC, constituent H3K27ac peaks, etc)
    and active genes (e.g. those with TPM > 1).
    """
    pass


@CRCminer.command(name="mine",
                  help="Identifies CRCs in a given sample.")
@click.option("--fasta", type=click.Path(),
              help="Genome FASTA file.",
              required=True)
@click.option("--enhancer", type=click.Path(),
              help="Path to ROSE2 output of annotated (super)enhancers.",
              required=True)
@click.option("--threshold", type=float, default=1e-4,
              help="p-value threshold used for determining significant motif matches.",
              required=True)
@click.option("--subpeaks", type=click.Path(),
              help="Path to BED file of regions to use for motif scanning, e.g. ATAC peaks. Will be limited to those that overlap with enhancers.",
              required=False)
@click.option("--active", type=click.Path(),
              help="File containing list of 'active' genes, one per line.",
              required=False)
@click.option("--mapping", type=click.Path(),
              help="Motif accession to gene ID mapping file.",
              required=False)
@click.option("--name", type=click.Path(), help="Analysis name, used to name output files and directory.")
def mine(fasta, enhancer, mapping):
    pass


@CRCminer.command(name="compare",
                  help="Compare output from two CRCminer 'mine' runs.")
@click.option("--sample1", type=click.Path(),
              help="CRCminer 'mine' output from one sample.",
              required=True)
@click.option("--sample2", type=click.Path(),
              help="CRCminer 'mine' output from another sample.",
              required=True)
def compare(sample1, sample2):
    pass


@CRCminer.command(name="report",
                  help="Interactive application to explore, visualize, and interpret CRCminer results.")
@click.option("--indir", type=click.Path(),
              help="Paths to one or more input directory containing CRCminer results.",
              required=True)
def report(indir):
    pass


if __name__ == "__main__":
    CRCminer()
