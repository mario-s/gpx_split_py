import os

import gpxpy
import gpxpy.gpx
from gpxpy.gpx import GPXTrack, GPXTrackSegment

from gpx_split.log_factory import LogFactory


class Writer:

    """
    This class will write a track segment into a gpx file.
    """

    def __init__(self, dest_dir):
        self.dest_dir = dest_dir
        self.logger = LogFactory.create(__name__)

    def write(self, name: str, segment: GPXTrackSegment):
        self.logger.debug(f"writing {len(segment.points)} points to {file}")
        gpx_track = gpxpy.gpx.GPXTrack()
        gpx_track.segments.append(segment)
        self.write_track(name, gpx_track)

    def write_track(self, name: str, track: GPXTrack):
        file = f"{name}.gpx"
        points = [point for segment in track.segments for point in segment.points]
        self.logger.debug(f"writing {len(points)} points to {file}")
        gpx = gpxpy.gpx.GPX()
        gpx.name = name
        gpx.tracks.append(track)

        with open(os.path.join(self.dest_dir, file), "w") as f:
            f.write(gpx.to_xml())
