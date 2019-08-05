import rtree
import copy
from shapely.ops import nearest_points
from shapely.geometry import LineString, Point

from allfed_spatial.geometry import intersects, closest_non_intersecting_within_radius
from allfed_spatial.features import Feature


def snap_features(r, features):
    """ Geometrically 'snap' (connect) features together which are within
    radius `r` of each other

    Arguments:
        r {int|float} -- Tolerance radius in metres within which to snap lines 
                   together
        features {list} -- list of Features

    Returns:
        list -- list of snapped Features
    """
    snapped_geoms = snap_linestrings(r, [f.geom for f in features])
    return [Feature(snapped_geoms[i], f.data) for i, f in enumerate(features)]


def intersects_with_index(rid, index, geom, geoms):
    """ Determines if a given geometry intersects any other supplied geometries
    by first using a spatial index to narrow down the search space

    Arguments:
        rid {int} -- index ID to exclude from search
        index {Index} -- spatial Index from rtrere
        geom {Shapely geometry} -- Query geometry
        geoms {list} -- List of Shapely geometries to check for intersection
            with

    Returns:
        boolean -- true if geom intersects one of geoms, false if not
    """
    buff = geom.buffer(1)
    ints = [geoms[int(i)] for i in index.intersection(buff.bounds) if i != rid]
    if any([intersects(ig, geom) for ig in ints]):
        return True
    return False


def snap_linestrings(r, lines):
    """ Geometrically 'snaps' LineStrings within an array together
    within a tolerance. An endpoint is only snapped if it is not
    otherwise connected.

    Arguments:
        r {int|float} -- Tolerance radius in metres within which to snap lines 
                   together
        lines {list} -- Array of Shapely LineStrings

    Returns:
        array -- Array of snapped Shapely LineStrings
    """

    # create an empty spatial index object
    index = rtree.index.Index()

    snapped = []

    # populate the spatial index
    for index_id, geom in enumerate(lines):
        index.insert(index_id, geom.bounds)

    # create snapped lines
    for search_id, geom in enumerate(lines):

        e1 = Point(geom.coords[0])
        e2 = Point(geom.coords[-1])
        new_geom = copy.deepcopy(geom)

        # endpoint 1
        if intersects_with_index(search_id, index, e1, lines):
            new_e1_coords = []
        else:
            e1buff = e1.buffer(r)
            e1_line_indices = [int(i) for i in index.intersection(
                e1buff.bounds) if i != search_id]

            if len(e1_line_indices) > 0:
                closest_line = closest_non_intersecting_within_radius(
                    e1, geom, [lines[i] for i in e1_line_indices], r)
                new_e1_coords = [nearest_points(e1, closest_line)[
                    1].coords[0]] if closest_line else []
            else:
                new_e1_coords = []

        # endpoint 2
        if intersects_with_index(search_id, index, e2, lines):
            new_e2_coords = []
        else:
            e2buff = e2.buffer(r)
            e2_line_indices = [int(i) for i in index.intersection(
                e2buff.bounds) if i != search_id]

            if len(e2_line_indices) > 0:
                closest_line = closest_non_intersecting_within_radius(
                    e1, geom, [lines[i] for i in e2_line_indices], r)
                new_e2_coords = [nearest_points(e2, closest_line)[
                    1].coords[0]] if closest_line else []
            else:
                new_e2_coords = []

        snapped_geom_coords = new_e1_coords + \
            [c for c in new_geom.coords] + new_e2_coords

        if len(snapped_geom_coords) == 3 and snapped_geom_coords[0] == snapped_geom_coords[-1]:
            snapped_geom_coords.pop(-1)

        snapped_geom = LineString(snapped_geom_coords)
        snapped.append(snapped_geom)
        index.delete(search_id, geom.bounds)
        index.insert(search_id, snapped_geom.bounds)
        lines[search_id] = snapped_geom

    return snapped
