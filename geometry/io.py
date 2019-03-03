import fiona
from shapely.geometry import mapping
from fiona.crs import from_epsg

def write_shape(geometries, data, schema, path):
    """ Write Shapely geometries to a specified path. Assumes geometries
    are in coordinate reference system EPSG 4326
    
    Arguments:
        geometries {list} -- Array of Shapely geometries
        data {list} -- Array of data dictionaries indexed to geometries
        schema {dict} -- Fiona schema for data
        path {str} -- Path to write to
    """

    with fiona.open(
            path, 
            'w', 
            crs=from_epsg(4326),
            driver='ESRI Shapefile',
            schema=schema
    ) as output:

        for i, g in enumerate(geometries):
            # attributes
            attributes = data[i]
            # write the row (geometry + attributes in GeoJSON format)
            output.write({'geometry': mapping(g), 'properties': attributes})