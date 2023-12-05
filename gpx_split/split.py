import logging
import time
from abc import ABC
from abc import abstractmethod
from pathlib import Path

import gpxpy
import gpxpy.gpx

from gpx_split.distance import GeoCalc
from gpx_split.log_factory import LogFactory


class Splitter(ABC):
    # for Meter in Kilometer.
    KILO = 1000

    """
    Base class to split a large gpx file into smaller chunks.
    """

    def __init__(self, writer):
        self.writer = writer
        self.logger = LogFactory.create(__name__)
        self.__reset_output_count()

    def __reset_output_count(self):
        self.output_count = 1

    def debug_enabled(func):
        def func_wrapper(self, name):
            if self.logger.isEnabledFor(logging.DEBUG):
                return func(self, name)
        return func_wrapper

    def next_name(self, source):
        name = Path(source).name.rsplit('.gpx')[0]
        return f"{name}_{self.output_count}"

    def new_segment(self, first_point = None):
        segment = gpxpy.gpx.GPXTrackSegment()
        if not first_point is None:
            segment.points.append(first_point)
        return segment

    def tracks(self, source):
        return self.parse(source).tracks

    def parse(self, source):
        with open(source, "rb") as f:
            gpx = gpxpy.parse(f)
        return gpx

    #ensure that we save file when number of all points is below max points per file
    def write_remainings(self, source, track_segment):
        if len(track_segment.points) > 1:
            self.write(source, track_segment)

    def write(self, source, track_segment):
        self.__log_track_len(track_segment)
        self.writer.write(self.next_name(source), track_segment)
        #increase counter after writing for the next name
        self.output_count += 1

    @debug_enabled
    def __log_track_len(self, track_segment):
        self.logger.debug(f"Track length: {self.track_length(track_segment)} km")

    def track_length(self, track_segment):
        """
        This calculates length of the track in km.
        """
        points = self.extract_coordinates(track_segment)
        return GeoCalc.track_length(points) / Splitter.KILO

    def extract_coordinates(self, track_segment):
        """
        Extract coordinates of all points.
        """
        return [(p.latitude, p.longitude) for p in track_segment.points]

    def log_source(self, source):
        self.logger.debug(f"Splitting file {source} into files in {self.writer.dest_dir}")

    def split(self, source, limit):
        self.log_source(source)

        self.__reset_output_count()
        track_segment = self.new_segment()

        for track in self.tracks(source):
            for segment in track.segments:
                for point in segment.points:
                    track_segment.points.append(point)

                    # if a limit for the track segment is exceeded,
                    # we write current segment to a file and create a new one
                    if self.exceeds_limit(track_segment, limit):
                        self.write(source, track_segment)
                        # add current point as first one to new segment
                        track_segment = self.new_segment(point)

        self.write_remainings(source, track_segment)

    @abstractmethod
    def exceeds_limit(self, track_segment, max):
        pass


class PointSplitter(Splitter):

    """
    This class splits a gpx file after a given number of points per segment is exceeded.
    """
    def split(self, source, limit):
        limit = limit or 500
        self.logger.debug(f"maximum number of points in track: {limit}")
        super().split(source, limit)

    def exceeds_limit(self, track_segment, limit):
        return len(track_segment.points) >= limit


class LengthSplitter(Splitter):

    """
    This class splits a gpx file after a given minimum length in km of segment is exceeded.
    """
    def __init__(self, writer):
        super().__init__(writer)
        self.segment_length = 0

    def split(self, source, limit):
        limit = limit or 20
        self.logger.debug(f"minimum track length: {limit} km")
        self.segment_length = 0
        super().split(source, limit)

    def exceeds_limit(self, track_segment, limit):
        if len(track_segment.points) > 2:
            points = self.extract_coordinates(track_segment)
            dist = GeoCalc.points(points[-2], points[-1]) / Splitter.KILO
            self.segment_length = self.segment_length + dist

            if self.segment_length >= limit:
                self.segment_length = 0
                return True
            return False

        return False