import rasterio
from affine import Affine
import numpy as np
import pyproj
from shapely.geometry import Point

from allfed_spatial.features.feature import Feature


def raster_to_features(path):
    """ Convert each pixel in a raster to a Shapely Point located at that 
    pixels centroid, and give it a value attribute equal to the pixels value.
    Return these as a list of Features.

    Arguments:
        path {str} -- Path to raster file

    Note: TODO potential way to vectorise:

    # All rows and columns into numpy mesh grid
    # cols, rows = np.meshgrid(np.arange(A.shape[2]), np.arange(A.shape[1]))

    # All eastings and northings
    # lats, lons = np.vectorize(rc2en, otypes=[np.float, np.float])(rows, cols)
    """

    # Read raster
    with rasterio.open(path) as r:
        T0 = r.transform  # upper-left pixel corner affine transform
        p1 = pyproj.Proj(r.crs)
        A = r.read()  # pixel values
        pixelSizeX, pixelSizeY = r.res

    # Get affine transform for pixel centres
    T1 = T0 * Affine.translation(0.5, 0.5)

    # Function to convert pixel row/column index (from 0) to lat/lon at centre
    def rc2en(r, c): return (c, r) * T1

    features = []
    it = np.nditer(A, flags=['multi_index'])

    while not it.finished:
        value = np.asscalar(it[0])
        if value > 0:
            features.append(Feature(
                Point(rc2en(it.multi_index[1], it.multi_index[2])),
                {
                    'value': np.asscalar(it[0]),
                    # assumes projected CRS
                    'pixel_size': (pixelSizeX * pixelSizeY) * 1e-6
                }
            ))
        it.iternext()

    return features
