from shapely.ops import split
from shapely.geometry import Point, MultiPolygon, LineString
import rtree
import math

from allfed_spatial.features.feature import Feature
from allfed_spatial.geometry.common import closest


def frechet_distance(points1, points2):
    """Test the distance between two lines
    Imagine if a person was walking their dog,
    and the person has to follow one line and the dog has to follow the other,
    how long does the leash need to be?
    https://en.wikipedia.org/wiki/Fr%C3%A9chet_distance

    Note:
    Currently this is a greedy implementation of moving along each line at the
    same proportional speed. So compare the point at 20% along line 1 with the
    point at 20% along line 2. Here we're just checking each point on both lines
    with the implicit point on the other line.

    Arguments:
        points1 {list} -- a list of points
        points2 {list} -- a list of points

    Returns:
        number - the distance between the lines
    """

    line1 = LineString(points1)
    line2 = LineString(points2)
    line1Len = line1.length
    line2Len = line2.length
    if (line1Len == 0):
        return max([points1[0].distance(p2) for p2 in points2])
    if (line2Len == 0):
        return max([points2[0].distance(p1) for p1 in points1])

    maxDist = max(
        points1[0].distance(points2[0]),
        points1[-1].distance(points2[-1]))
    line1PointIndex = 1
    line2PointIndex = 1
    line1PrevSegLength = 0.0
    line2PrevSegLength = 0.0

    while (line1PointIndex < len(points1) and line2PointIndex < len(points2)):
        line1Seg = LineString([
            points1[line1PointIndex - 1],
            points1[line1PointIndex]
        ])
        line2Seg = LineString([
            points2[line2PointIndex - 1],
            points2[line2PointIndex]
        ])

        line1NextSegLength = line1Seg.length + line1PrevSegLength
        line2NextSegLength = line2Seg.length + line2PrevSegLength

        if ((line1NextSegLength / line1Len) < (line2NextSegLength / line2Len)):
            line2Implicit = line2Seg.interpolate(
                (line2Len * line1NextSegLength / line1Len) - line2PrevSegLength,
                normalized = False)
            maxDist = max(
                maxDist,
                points1[line1PointIndex].distance(line2Implicit))
            line1PointIndex += 1
            line1PrevSegLength = line1NextSegLength
        else:
            line1Implicit = line1Seg.interpolate(
                (line1Len * line2NextSegLength / line2Len) - line1PrevSegLength,
                normalized = False)
            maxDist = max(
                maxDist,
                points2[line2PointIndex].distance(line1Implicit))
            line2PointIndex += 1
            line2PrevSegLength = line2NextSegLength

    return maxDist


def make_points_on_line(geom, distance):
    """ Create points evenly distributed along a line at a fixed distance.
    Note that lines w/points will not meet Shapely's intersection criteria
    due to the use of interpolate.

    Arguments:
        geom {LineString|MultiLineString} -- geom to create points along
        distance {int|float} -- distance in metres along line to split

    Returns:
        list -- list of shapely Points
    """

    if geom.geom_type == 'LineString':
        num_vert = max(int(math.ceil(geom.length / distance) - 1), 1)
        line_fraction = 1 / (num_vert + 1)
        return [
            geom.interpolate(n * line_fraction, normalized=True)
            for n in range(1, num_vert + 1)
        ]
    elif geom.geom_type == 'MultiLineString':
        parts = [make_points_on_line(part, distance)
                 for part in geom]
        return [point for part in parts for point in part]
    else:
        raise ValueError('unhandled geometry %s', (geom.geom_type,))


def split_features_by_distance(features, distance):
    """ Split up each geometry in a list of features based on distance

    Arguments:
        features {list} -- List of Feature objects
        distance {int|float} -- Approx distance in metres between splits
    """
    split_features = []
    for f in features:
        split_geoms = split_line_by_distance(f.geom, distance)
        for sg in split_geoms:
            split_features.append(Feature(sg, f.data))
    return split_features


def split_line_by_distance(geom, distance):
    """ Break up Shapely LineString into multiple Shapely LineStrings based
    on a fixed distance in metres. Won't always exactly distribute lines
    according to specified distance, but will attempt to approximate it.

    Arguments:
        geom {LineString} -- line to split up
        distance {int|float} -- approx distance in metres between splits

    Returns:
        list -- list of LineStrings corresponding to split line segments
    """

    if geom.length < distance:
        return [geom]

    # Interpolated points won't intersect line, so need to buffer
    r = distance / 100
    buffed = MultiPolygon(
        [p.buffer(r) for p in make_points_on_line(geom, distance)]
    )

    # Buffered polygons will each yield two additional split line sections
    poly_split_lines = split(geom, buffed)

    # Stitch together each two additional split line sections into one
    point_split_lines = []
    for i, current_line in enumerate(poly_split_lines):

        if i == len(poly_split_lines) - 1:  # last line
            point_split_lines.append(current_line)
        elif i % 2 == 0:  # 0 or even
            last_line = current_line
        else:
            point_split_lines.append(LineString(
                list(last_line.coords) + list(current_line.coords)))
            last_line = current_line

    return point_split_lines


def join_points_to_lines(points, lines):
    """ Create Shapely LineStrings joining each provided point to the closest
    endpoint within the provided line geometries.

    Arguments:
        points {list} -- list of Shapely Points
        lines {list} -- list of Shapely Linestrings

    Returns:
        [list] -- list of Shapely Linestrings joining points to lines
    """

    # create an empty spatial index object
    index = rtree.index.Index()

    # populate the spatial index
    for index_id, geom in enumerate(lines):
        index.insert(index_id, geom.bounds)

    # create lines which join points to lines
    joins = []
    for search_id, geom in enumerate(points):

        # buffer out the point until we hit a line
        r = 1
        index_ids = []

        while len(index_ids) == 0:
            buffered = geom.buffer(r)
            index_ids = [int(i) for i in index.intersection(buffered.bounds)]
            r *= 2

        points_in_lines = []
        for l in [lines[ind] for ind in index_ids]:
            points_in_lines.append(Point(l.coords[0]))
            points_in_lines.append(Point(l.coords[-1]))

        closest_point_on_line = closest(geom, points_in_lines)
        joins.append(LineString((geom, closest_point_on_line)))

    return joins
