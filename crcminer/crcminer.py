import click
# Command Group
@click.group(name='CRCminer')
def cli_tools():
    """Tool related commands"""
    pass

@cli_tools.command(name='mine', help='mines for CRC')
@click.option('--fasta', type=click.Path(),help='Genome FASTA file.')
@click.option('--enhancer', type=click.Path(), help='ROSE2 output of annotated (super)enhancers.')
@click.option('--subpeaks', type=click.Path(), help='BED file of regions to use for motif scanning, e.g. ATAC peaks. Will be limited to those that overlap with enhancers.')
@click.option('--mapping', type=click.Path(), help='Motif accession to gene ID mapping file.')
def test(fasta,enhancer,mapping):
    pass

@cli_tools.command(name='compare', help='Compare output from two CRCminer mine runs')
@click.option('--edgelist1', type=click.Path(), help='edgelist from sampleX')
@click.option('--edgelist2', type=click.Path(), help='edgelist from sampleY')
def test2(edgelist1,edgelist2):
    pass

@cli_tools.command(name='report', help='report vizualization')
@click.option('--indir',type=click.Path(),help='Input directory containing CRCminer results.')
def test3(indir):
    pass

# todo 
# add more description

if __name__ == '__main__':
    cli_tools()
