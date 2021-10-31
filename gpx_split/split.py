import logging
from abc import ABC
from pathlib import Path

import gpxpy
import gpxpy.gpx

from gpx_split.distance import GeoCalc
from gpx_split.log_factory import LogFactory


class Splitter(ABC):

    """
    Base class to split a large gpx file into smaller chunks.
    """

    def __init__(self, writer):
        self.writer = writer
        self.logger = LogFactory.create(__name__)

    def debug_enabled(func):
        def func_wrapper(self, name):
            if self.logger.isEnabledFor(logging.DEBUG):
                return func(self, name)
        return func_wrapper

    def next_name(self, source):
        name = Path(source).name.rsplit('.gpx')[0]
        return lambda count: f"{name}_{str(count)}"

    def new_segment(self):
        return gpxpy.gpx.GPXTrackSegment()

    def tracks(self, source):
        return self.parse(source).tracks

    def parse(self, source):
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

    def log_source(self, source):
        self.logger.debug(f"Splitting file {source} into files in {self.writer.dest_dir}")


class PointSplitter(Splitter):

    """
    This class split a gpx file after a given number of points per segment is exceeded.
    """

    def split(self, source, max_segment_points=500):
        self.log_source(source)

        output_count = 1
        next_name = self.next_name(source)
        track_segment = self.new_segment()

        for track in self.tracks(source):
            for segment in track.segments:
                for point in segment.points:
                    track_segment.points.append(point)

                    if len(track_segment.points) >= max_segment_points:
                        self.write(next_name(output_count), track_segment)
                        output_count += 1
                        track_segment = self.new_segment()
                        track_segment.points.append(point)

        self.write_remainings(next_name(output_count), track_segment)