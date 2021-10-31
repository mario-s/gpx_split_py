import logging
from pathlib import Path

import gpxpy
import gpxpy.gpx

from gpx_split.distance import GeoCalc
from gpx_split.log_factory import LogFactory


class Splitter:

    """
    This class will split a large gpx file into smaller chunks.
    """

    def __init__(self, writer):
        self.writer = writer
        self.logger = LogFactory.create(__name__)

    def debug_enabled(func):
        def func_wrapper(self, name):
            if self.logger.isEnabledFor(logging.DEBUG):
                return func(self, name)
        return func_wrapper

    def split(self, source, max_segment_points=500):
        self.logger.debug(f"Splitting file {source} into files in {self.writer.dest_dir}")

        next_name = Splitter.next_name(source)
        output_count = 1
        track_segment = Splitter.new_segment()

        for track in Splitter.tracks(source):
            for segment in track.segments:
                for point in segment.points:
                    track_segment.points.append(point)

                    if len(track_segment.points) >= max_segment_points:
                        self.write(next_name(output_count), track_segment)
                        output_count += 1
                        track_segment = Splitter.new_segment()
                        track_segment.points.append(point)

        self.write_remainings(next_name(output_count), track_segment)

    @classmethod
    def next_name(cls, source):
        name = Path(source).name.rsplit('.gpx')[0]
        return lambda count: f"{name}_{str(count)}"

    @classmethod
    def new_segment(cls):
        return gpxpy.gpx.GPXTrackSegment()

    @classmethod
    def tracks(cls, source):
        return Splitter.parse(source).tracks

    @classmethod
    def parse(cls, source):
        with open(source, "rb") as f:
            gpx = gpxpy.parse(f)
        return gpx

    #ensure that we save file when number of all points is below max points per file
    def write_remainings(self, name, track_segment):
        if len(track_segment.points) > 1:
            self.write(name, track_segment)

    def write(self, name, track_segment):
        self.__log_track_len(track_segment)
        self.writer.write(name, track_segment)

    @debug_enabled
    def __log_track_len(self, track_segment):
        points = [(p.latitude, p.longitude) for p in track_segment.points]
        self.logger.debug(f"Track length: {GeoCalc.track_length(points) / 1000} km")
