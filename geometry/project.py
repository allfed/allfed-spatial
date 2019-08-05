import pyproj
from shapely.ops import transform
from functools import partial

# Functions for detaling with coordinate referencee systems (CRS) and
# converting between them. See the following link for an introduction
# to these concepts:
# https://docs.qgis.org/3.4/en/docs/gentle_gis_introduction/coordinate_reference_systems.html

# https://epsg.io/54002 is equal distance
WORLD_PROJECTION_STRING = '+proj=eqc +lat_ts=60 +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs'

# 54034 is equal area

# TODO sort out utm functions


def project_to_utm(geoms, zone, hemisphere):
    project_to_utm = partial(
        pyproj.transform,
        pyproj.Proj(init='epsg:4326'),
        pyproj.Proj(
            f"+proj=utm +zone={zone}, +ellps=WGS84 +datum=WGS84 +units=m +no_defs")
    )
    return [transform(project_to_utm, geom) for geom in geoms]


def project_from_utm(geoms, epsg, zone):
    project_from_utm = partial(
        pyproj.transform,
        pyproj.Proj(init=f"epsg:{epsg}", proj="utm", zone=zone),
        pyproj.Proj(init='epsg:4326')
    )
    return [transform(project_from_utm, geom) for geom in geoms]


def project_features_to_utm(features, zone):
    project_to_utm = partial(
        pyproj.transform,
        pyproj.Proj(init='epsg:4326'),
        pyproj.Proj(
            f"+proj=utm +zone={zone}, +ellps=WGS84 +datum=WGS84 +units=m +no_defs")
    )
    for f in features:
        f.geom = transform(project_to_utm, f.geom)


# def project_features_to_utm(features, epsg, zone):
#     project_to_utm = partial(
#         pyproj.transform,
#         pyproj.Proj(init='epsg:4326'),
#         pyproj.Proj(init=f"epsg:{epsg}", proj="utm", zone=zone)
#     )
#     for f in features:
#         f.geom = transform(project_to_utm, f.geom)


def project_features_from_utm(features, epsg, zone):
    project_from_utm = partial(
        pyproj.transform,
        pyproj.Proj(init=f"epsg:{epsg}", proj="utm", zone=zone),
        pyproj.Proj(init='epsg:4326')
    )
    for f in features:
        f.geom = transform(project_from_utm, f.geom)


def project_features_to_world(features, projection=WORLD_PROJECTION_STRING):
    """ Project features from a lat/lon CRS (epsg:4326) defined in degrees
    to a projected CRS defined in metres based on the WORLD_PROJECTION_STRING
    config parameter by default.

    Arguments:
        features {list} -- list of features in EPSG:4326 to project
    """
    project_to_utm = partial(
        pyproj.transform,
        pyproj.Proj(init='epsg:4326'),
        pyproj.Proj(projection)
    )
    for f in features:
        f.geom = transform(project_to_utm, f.geom)


def project_features_from_world(features, projection=WORLD_PROJECTION_STRING):
    """Project features from a projecteed CRS defined in metres to a lat/lon
    CRS defined in degrees based on the WORLD_PROJECTION_STRING
    config parameter by default.

    Arguments:
        features {list} -- list of features in `projection` to project
    """
    project_from_utm = partial(
        pyproj.transform,
        pyproj.Proj(WORLD_PROJECTION_STRING),
        pyproj.Proj(init='epsg:4326')
    )
    for f in features:
        f.geom = transform(project_from_utm, f.geom)
