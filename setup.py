from setuptools import find_packages, setup

setup(
    name='allfed-spatial',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'fiona',
        'shapely',
        'pyproj',
        'rasterio',
        'rtree',
        'ortools',
        'affine',
        'numpy',
        'fuzzywuzzy'
    ],
    url='https://github.com/allfed/allfed-spatial',
    license='MIT',
    author='ALLFED',
    author_email='tim.fist@allfed.info',
    description='Helper code for spatial data processing and analysis in ALLFED projects  '
)
