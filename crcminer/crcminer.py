import click
# Command Group
@click.group(name='CRCminer')
def cli_tools():
    """Tool related commands"""
    pass

@cli_tools.command(name='mine', help='mines for CRC')
@click.option('--fasta', type=click.Path(),help='Genome FASTA file.')
@click.option('--enhancer', type=click.Path(), help='Path to ROSE2 output of annotated (super)enhancers.')
@click.option('--subpeaks', type=click.Path(), help='Path to BED file of regions to use for motif scanning, e.g. ATAC peaks. Will be limited to those that overlap with enhancers.')
@click.option('--active', type=click.Path(), help='File containing list of "active" genes, one per line.')
@click.option('--mapping', type=click.Path(), help='Motif accession to gene ID mapping file.')
@click.option('--threshold', type=float, default = 1e-4, help='p-value threshold used for determing significant motif matches.')
@click.option('--name', type=click.Path(), help='Analysis name, used to name output files and directory.')
def test(fasta,enhancer,mapping):
    pass

@cli_tools.command(name='compare', help='Compare output from two CRCminer mine runs')
@click.option('--sample1', type=click.Path(), help='CRCminer mine output from one sample.')
@click.option('--sample2', type=click.Path(), help='CRCminer mine output from another sample.')
def test2(sample1,sample2):
    pass

@cli_tools.command(name='report', help='Interactive application to explore, visualize, and interpret CRCminer results.')
@click.option('--indir',type=click.Path(),help='Paths to one or more input directory containing CRCminer results.')
def test3(indir):
    pass

# todo 
# add more description

if __name__ == '__main__':
    cli_tools()
