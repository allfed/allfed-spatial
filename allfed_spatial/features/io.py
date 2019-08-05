import fiona
from shapely.geometry import mapping, LineString, Polygon, Point, shape, MultiPolygon
from fiona.crs import from_epsg

from allfed_spatial.features import Feature


def get_fiona_type(value):
    if isinstance(value, str):
        return 'str:250'
    elif isinstance(value, int):
        return 'int:16'
    elif isinstance(value, float):
        return 'float:16'
    else:
        raise ValueError('Unknown type: {}'.format(type(value)))


def get_shapely_class_from_geom_type(geom_type):
    if geom_type == 'LineString':
        return LineString
    if geom_type == 'Point':
        return Point
    if geom_type == 'Polygon':
        return Polygon
    if geom_type == 'MultiPolygon':
        return MultiPolygon
    raise ValueError('Geometry type {} not recognised'.format(geom_type))


def load_features(path, data=False):
    """ From a shapefile, create a list of features with geometry and data
    loaded from file. If data is specified, data will instead be filled with
    whatever is provided.

    Arguments:
        path {str} -- Path to shapefile to load
        data {boolean|dict} -- False, or value to fill each feature's data with
    """
    features = []
    with fiona.open(path) as source:
        for f in source:
            if not f['geometry']:
                print('Ignoring feature with no geometry...')
                continue
            shapely_class = get_shapely_class_from_geom_type(
                f['geometry']['type'])
            features.append(Feature(
                shapely_class(shape(f['geometry'])),
                data if data else dict(f['properties'])
            ))
    return features


def get_feature_schema(feature):
    """ Get the Fiona schema from a Feature

    Arguments:
        feature {Feature} -- Feature object

    Returns:
        dict -- Corresponding Fiona schema
    """

    return {
        'geometry': feature.geom.type,
        'properties': {
            key: get_fiona_type(value) for key, value in feature.data.items()
        }
    }


def write_features(features, path):
    """ Write Features to specified path. Assumes geometries
    are in coordinate reference system EPSG 4326

    Arguments:
        features {list} -- list of Features
        path {str} -- Path to write to
    """
    output_driver = "GPKG"

    with fiona.open(
            path,
            'w',
            crs=from_epsg(4326),
            driver=output_driver,
            schema=get_feature_schema(features[0]),
            encoding='utf-8'
    ) as output:

        for f in features:
            # write the row (geometry + attributes in GeoJSON format)
            output.write({'geometry': mapping(f.geom), 'properties': f.data})


def write_shape(geometries, data, schema, path):
    """ Write Shapely geometries to a specified path. Assumes geometries
    are in coordinate reference system EPSG 4326

    Arguments:
        geometries {list} -- Array of Shapely geometries
        data {list} -- Array of data dictionaries indexed to geometries
        schema {dict} -- Fiona schema for data
        path {str} -- Path to write to
    """
    output_driver = "GeoPackage"

    with fiona.open(
        path,
        'w',
        crs=from_epsg(4326),
        driver=output_driver,
        schema=schema,
        encoding='utf-8'
    ) as output:

        for i, g in enumerate(geometries):
            # attributes
            attributes = data[i]
            # write the row (geometry + attributes in GeoJSON format)
            output.write({'geometry': mapping(g), 'properties': attributes})
