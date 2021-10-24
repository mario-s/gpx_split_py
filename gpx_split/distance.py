import gpxpy.geo as geo

class GeoCalc:

    """
    This class support geodesic calculation.
    """

    def points(p1, p2):
        """
        Distance between two points in meter.
        """
        return geo.haversine_distance(p1[0], p1[1], p2[0], p2[1])

    def track_length(points):
        """
        Length of a track in meter.
        """
        len = 0
        prev_point = None
        for p in points:
            if not prev_point is None:
                len += GeoCalc.points(prev_point, p)
            prev_point = p
        return len
