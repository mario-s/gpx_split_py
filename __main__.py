import click
import time
import logging
from gpx_split.log_factory import LogFactory

from gpx_split.split import PointSplitter, LengthSplitter
from gpx_split.writer import Writer

@click.command()
@click.argument("source")
@click.option("-o", "--output", help="Output directory", default=".")
@click.option("-t", "--type", type=click.Choice(["p", "l"]),
    help="split type: points per track (p) | length of track (l)",
    default="p")
@click.option("-l", "--limit", type=int,
    help="The track will be split when the limit is exceeded, points or length.")
@click.option("-d", "--debug", help="Debug Log output.", default=False)
def _main(source, output, type, limit, debug):
    start = time.time()
    logger = LogFactory.create(__name__)

    writer = Writer(output)
    if type == "p":
        splitter = PointSplitter(writer)
    else:
        splitter = LengthSplitter(writer)

    if debug:
        logger.setLevel(logging.DEBUG)
        writer.logger.setLevel(logging.DEBUG)
        splitter.logger.setLevel(logging.DEBUG)

    splitter.split(source, limit)

    logger.debug(f"Execution time: {time.time() - start} seconds")


if __name__ == "__main__":
    _main()
