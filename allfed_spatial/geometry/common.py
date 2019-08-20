
def closest(geom, targets, n=1):
    """ Finds the `n`th closest geometry to geom within targets.
    For example, if n=2, finds the member of targets which is the 2nd closest 
    to geom. 

    Arguments:
        geom {Shapely geometry} -- A single Shapely geometry (e.g. Point)
        targets {list} -- A list of Shaopely geometries

    Keyword Arguments:
        n {int} -- The `n`th closest geometry to return (default: {1})

    Returns:
        Shapely geometry -- Member of targets which is the `n`th closest
    """
    if len(targets) < n:
        raise ValueError(
            'List of targets needs at least {} members'.format(n)
        )

    def distance(t): return geom.distance(t)
    return sorted(targets, key=distance)[n - 1]


def closest_within_radius(geom, targets, radius, n=1):
    """Finds the `n`th closest geometry to geom within targets within a
    defined radius of geom. For example, if n=2 and r=10, finds the member of
    targets which is the 2nd closest to geom, which is also within 10m of
    geom. If there are not `n` candidates from targets within the radius then 
    None is returned.

    Arguments:
        geom {Shapely geometry} -- A single Shapely geometry (e.g. Point)
        targets {list} -- A list of Shaopely geometries
        radius {int|float} -- Distance from geom to search within

    Keyword Arguments:
        n {int} -- The `n`th closest geometry to return (default: {1})

    Returns:
        Shapely geometry | None -- Member of targets which is `n`th closest
            within the radius
    """
    most_close = closest(geom, targets, n)
    if geom.distance(most_close) > radius:
        return None
    return most_close


def closest_non_intersecting_within_radius(
        geom, non_intersect_geom, targets, radius, n=1):
    """ Finds the `n`th closest geometry to geom within targets within a
    defined radius of geom, which also does not intersect non_intersect_geom.
    See closest_within_radius for more info on radius condition.

    Arguments:
        geom {Shapely geometry} -- A single Shapely geometry (e.g. Point)
        non_intersect_geom {Shapely geometry} -- A single Shapely geometry 
        targets {list} -- A list of Shaopely geometries
        radius {int|float} -- Distance from geom to search within

    Keyword Arguments:
        n {int} -- The `n`th closest geometry to return (default: {1})

    Returns:
        Shapely geometry | None -- Member of targets which is `n`th closest
            within the radius, which also doesn't intersect non_intersect_geom
    """
    if len(targets) < n:
        raise ValueError(
            'List of targets needs at least {n} members'.format(n)
        )

    eligible = list(filter(lambda t: not intersects(
        non_intersect_geom, t), targets))

    if len(eligible) > 0:
        most_close = closest(geom, eligible, n)
        if geom.distance(most_close) > radius:
            return None
        return most_close
    return None


def intersects(g1, g2):
    """ Determine if g1 geometrically intersects g2

    Arguments:
        g1 {Shapely geometry} -- A single Shapely geometry (e.g. Polygon)
        g2 {Shapely geometry} -- A single Shapely geometry (e.g. Point)

    Returns:
        boolean -- true if g1 intersects g2, false otherwise
    """
    return g1.distance(g2) < 1e-8
