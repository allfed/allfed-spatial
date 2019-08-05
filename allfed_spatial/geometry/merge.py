from shapely.ops import linemerge

from allfed_spatial.features.feature import Feature


def merge_features(features):
    """ Merge feature geometries together where possible, forming several
    contiguous MultiLineStrings. Applies data of first feature to all.

    Arguments:
        features {list} -- list of Features
    """
    merged_features = []
    merged_geoms = linemerge([f.geom for f in features])

    if merged_geoms.geom_type == 'MultiLineString':
        merged_geoms = merged_geoms.geoms
    else:
        merged_geoms = [merged_geoms]

    for mg in merged_geoms:
        merged_features.append(Feature(mg, features[0].data))

    return merged_features
