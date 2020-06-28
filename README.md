# 🍇 allfed-spatial

Helper code for spatial data processing and analysis in ALLFED projects


## Setup

Before any of the following steps, you will first need
to obtain `libspatialindex`, which can be installed on MacOS as follows:

```brew install spatialindex```

Installation for Windows and *nix systems can be found here:
http://toblerity.org/rtree/install.html

### Importing as a package

To install `allfed_spatial` as a Python package:

```pip install git+https://github.com/allfed/allfed-spatial.git#egg=allfed-spatial```

You may then import any of the modules in this repo as normal, e.g.

```from allfed_spatial.operations.consume import consume```

### Development setup

To set up dependencies for development of `allfed_spatial` (recommend using
Python 3.7.7)

```pip install -r requirements.txt```

Tests can be run using `nose`:

```nosetests```
