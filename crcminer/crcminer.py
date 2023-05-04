import click


# Command Group
@click.group(name='CRCminer')
def cli_tools():
    """Tool related commands"""
    pass

@cli_tools.command(name='mine', help='mines for CRC')
@click.option('--fasta', help='fasta')
@click.option('--enhancer', help='ROSE2 output of annotated (super)enhancers')
@click.option('--mapping', help='Motif ID to gene ID mapping file.')
def test(fasta,enchancer,mapping):
    pass

@cli_tools.command(name='compare', help='compare two networks')
@click.option('--edgelist1',help='edgelist from sampleX')
@click.option('--edgelist2',help='edgelist from sampleY')
def test2(edgelist1,edgelist2):
    pass

@cli_tools.command(name='report', help='report vizualization')
@click.option('--indir',help='input directory CRCminer results')

def test3(indir):
    pass

if __name__ == '__main__':
    cli_tools()