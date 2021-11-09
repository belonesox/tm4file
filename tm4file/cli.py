"""Console script for tm4file."""
import sys
import click
from .tm4file import Time4Files
 

@click.command()
@click.argument('dir4import')
@click.option('--recode', '-r', is_flag=True, help="Recode video using NVENC lossless")
def main(dir4import, recode):
    """Console script for tm4file."""
    processor = Time4Files(recode)
    processor.process(dir4import)
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
