import click
import logging

from gpx_split.split import Splitter
from gpx_split.writer import Writer

@click.command()
@click.argument("source")
@click.option("-o", "--output", help="Output directory", default=".")
@click.option("-p", "--points",
    help="Maximum number of points per result file.", default=500)
@click.option("-l", "--log", help="Log output.", default=False)
def _main(source, output, points, log):
    writer = Writer(output)
    splitter = Splitter(writer)
    if log:
        writer.logger.setLevel(logging.DEBUG)
        splitter.logger.setLevel(logging.DEBUG)

    splitter.split(source, max_segment_points=points)

if __name__ == "__main__":
    _main()
