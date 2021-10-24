import os

import gpxpy
import gpxpy.gpx

from gpx_split.log_factory import LogFactory


class Writer:

    """
    This class will write a track segment into a gpx file.
    """

    def __init__(self, dest_dir):
        self.dest_dir = dest_dir
        self.logger = LogFactory.create(__name__)

    def write(self, name, segment):
        file = f"{name}.gpx"
        self.logger.debug(f"writing {len(segment.points)} points to {file}")
        gpx = gpxpy.gpx.GPX()
        gpx.name = name
        gpx_track = gpxpy.gpx.GPXTrack()
        gpx.tracks.append(gpx_track)
        gpx_track.segments.append(segment)

        with open(os.path.join(self.dest_dir, file), "w") as f:
            f.write(gpx.to_xml())
