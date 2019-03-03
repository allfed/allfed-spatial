import pyproj
from shapely.ops import transform
from functools import partial

def project_to_utm(geoms, epsg, zone):
    project_to_utm = partial(
        pyproj.transform, 
        pyproj.Proj(init='epsg:4326'),
        pyproj.Proj(init=f"epsg:{epsg}", proj="utm", zone=zone)
    )
    return [transform(project_to_utm, geom) for geom in geoms]

def project_from_utm(geoms, epsg, zone):
    project_from_utm = partial(
        pyproj.transform, 
        pyproj.Proj(init=f"epsg:{epsg}", proj="utm", zone=zone),
        pyproj.Proj(init='epsg:4326')
    )
    return [transform(project_from_utm, geom) for geom in geoms]