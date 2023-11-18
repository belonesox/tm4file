"""Console script for tm4file."""
import sys
import click
from .tm4file import Time4Files
 

@click.command()
@click.argument('dir4import')
@click.option('--recode', '-r', is_flag=True, help="Recode video using NVENC lossless")
@click.option('--meta', '-m', is_flag=True, help="Try to use metadata (EXIF, etc) to get creation time")
# @click.option('--lightmeta', '-l', is_flag=True, help="«Light Meta» mode - use metadata if filename not begin with 'YYYY-MM-DD'")
@click.option('--noimage', '-n', is_flag=True, help="Ignore images, import only video")
def main(dir4import, recode, meta, noimage):
    """Console script for tm4file."""
    processor = Time4Files(recode, meta, noimage)
    processor.process(dir4import)
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
