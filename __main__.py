import click
import logging

from gpx_split.split import PointSplitter, LengthSplitter
from gpx_split.writer import Writer

@click.command()
@click.argument("source")
@click.option("-o", "--output", help="Output directory", default=".")
@click.option("-t", "--type", type=click.Choice(["p", "l"]),
    help="split type: points per track (p) | length of track (l)",
    default="p")
@click.option("-m", "--max", type=int,
    help="Maximum when track shall be splitted, can be points or length in km.")
@click.option("-d", "--debug", help="Debug Log output.", default=False)
def _main(source, output, type, max, debug):
    writer = Writer(output)
    if type == "p":
        splitter = PointSplitter(writer)
    else:
        splitter = LengthSplitter(writer)
    if debug:
        writer.logger.setLevel(logging.DEBUG)
        splitter.logger.setLevel(logging.DEBUG)

    splitter.split(source, max)

if __name__ == "__main__":
    _main()
