from shapely.ops import split
from shapely.geometry import Point, MultiPolygon, LineString
import rtree
import math

from allfed_spatial.features.feature import Feature
from allfed_spatial.geometry.common import closest


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
        return type(geom)([p for p in parts if not p.is_empty])
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
