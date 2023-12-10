import logging
from abc import ABC
from abc import abstractmethod
from pathlib import Path

import gpxpy
import gpxpy.gpx
from gpxpy.gpx import GPXTrack, GPXTrackSegment

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

    def clone_track(self, src_track, points) -> GPXTrack:
        segment = GPXTrackSegment()
        segment.points = points
        cloned_track = src_track
        cloned_track.segments = [segment]
        return cloned_track

    def tracks(self, source):
        return self.parse(source).tracks

    def parse(self, source):
        with open(source, "rb") as f:
            gpx = gpxpy.parse(f)
        return gpx

    def write(self, source, track):
        self.__log_track_len(track)
        self.writer.write_track(self.next_name(source), track)
        #increase counter after writing for the next name
        self.output_count += 1

    @debug_enabled
    def __log_track_len(self, track):
        self.logger.debug(f"Track length: {self.track_length(track)} km")

    def track_length(self, track):
        """
        This calculates length of the track in km.
        """
        points = [point for segment in track.segments for point in segment.points]
        coords = self.extract_coordinates(points)
        return GeoCalc.track_length(coords) / Splitter.KILO

    def extract_coordinates(self, points):
        """
        Extract coordinates of all points.
        """
        return [(p.latitude, p.longitude) for p in points]

    def log_source(self, source):
        self.logger.debug(f"Splitting file {source} into files in {self.writer.dest_dir}")

    def split(self, source, limit):
        self.log_source(source)
        self.__reset_output_count()

        origin = self.tracks(source)
        new_tracks = self._split(origin, limit)
        if len(new_tracks) > len(origin):
            for track in new_tracks:
                self.write(source, track)

    def _split(self, tracks, limit) -> [GPXTrack]:
        new_tracks = []
        points = []

        for track in tracks:
            for segment in track.segments:
                for point in segment.points:
                    points.append(point)

                    # if a limit for the track segment is exceeded,
                    # we write current segment to a file and create a new one
                    if self.exceeds_limit(points, limit):
                        new_track = self.clone_track(track, points)
                        new_tracks.append(new_track)

                        # add current point as first one to new segment
                        points = [point]

        if len(points) > 1:
            last = tracks[-1]
            new_track = self.clone_track(last, points)
            new_tracks.append(new_track)

        return new_tracks

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

    def exceeds_limit(self, points, limit):
        return len(points) >= limit


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

    def exceeds_limit(self, points, limit):
        if len(points) > 2:
            coords = self.extract_coordinates(points)
            dist = GeoCalc.points(coords[-2], coords[-1]) / Splitter.KILO
            self.segment_length = self.segment_length + dist

            if self.segment_length >= limit:
                self.segment_length = 0
                return True
            return False

        return False