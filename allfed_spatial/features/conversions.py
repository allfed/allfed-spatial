import geopandas as gpd


def features_to_geodataframe(features: list) -> gpd.GeoDataFrame:
    """
    Convert a list of features into a GeoPandas data frame

    :param features: list of Features
    :return: geodataframe corresponding to the feature list
    """
    return gpd.GeoDataFrame(
        [f.data for f in features],
        geometry=[f.geom for f in features]
    )



