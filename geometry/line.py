from shapely.ops import nearest_points, split, snap
from shapely.geometry import MultiPoint, MultiPolygon, LineString
import rtree

def make_points_on_line(geom, distance):
    """ Create points along a line at a fixed distance. Note that lines
    will not meet Shapely's intersection criteria due to the use of 
    interpolate.
    
    Arguments:
        geom {LineString|MultiLineString} -- geom to create pointsa long
        distance {int|float} -- distance in metres along line to split
    
    Returns:
        list -- list of shapely Points
    """

    if geom.geom_type == 'LineString':
        num_vert = int(round(geom.length / distance))
        if num_vert == 0:
            num_vert = 1
        return [
            geom.interpolate(float(n) / num_vert, normalized=True)
            for n in range(num_vert + 1)
        ]
    elif geom.geom_type == 'MultiLineString':
        parts = [make_points_on_line(part, distance)
                 for part in geom]
        return type(geom)([p for p in parts if not p.is_empty])
    else:
        raise ValueError('unhandled geometry %s', (geom.geom_type,))

        
def split_line_by_distance(geom, distance):
    """ Break up Shapely LineString into multiple Shapely LineStrings based
    on a fixed distance in metres. Won't always exactly distribute lines
    according to specified distance, but will attempt to approximate it.
    
    Arguments:
        geom {LineString} -- line to split up
        distance {int|float} -- approx distance in metres between splits
    
    Returns:
        list -- list of LineStrings corresponding to split line segments
    """

    # Interpolated points won't intersect line, so need to buffer
    r = distance / 100;
    buffed = MultiPolygon(
        [p.buffer(r) for p in make_points_on_line(geom, distance)]
    )
    
    # Buffered polygons will each yield two additional split line sections
    poly_split_lines = split(geom, buffed)

    # Stitch together each two additional split line sections into one
    point_split_lines = []
    for i, current_line in enumerate(poly_split_lines):
        
        if i == len(poly_split_lines) - 1: # last line
            point_split_lines.append(current_line)
        elif i % 2 == 0: # 0 or even
            last_line = current_line
        else:
            point_split_lines.append(LineString(list(last_line.coords) + list(current_line.coords)))
            last_line = current_line
    
    return point_split_lines
    

def join_points_to_lines(points, lines):
    """ Create Shapely LineStrings joining each provided point to the closest
    endpoint within the provided line geometries.
    
    Arguments:
        points {list} -- list of Shapely Points
        lines {list} -- list of Shapely Linestrings
    
    Returns:
        [list] -- list of Shapely Linestrings joining points to lines
    """
    
    # create an empty spatial index object
    index = rtree.index.Index()
    
    # populate the spatial index
    for index_id, geom in enumerate(lines):
        index.insert(index_id, geom.bounds)
    
    # create lines which join points to lines
    joins = []
    for search_id, geom in enumerate(points):
        
        # buffer out the point until we hit a line
        r = 1
        index_ids = []
        
        while len(index_ids) == 0:  
            buffered = geom.buffer(r)
            index_ids = [int(i) for i in index.intersection(buffered.bounds)]
            r *= 2

        closest_line = lines[index_ids[0]]  # doesn't seem to work well
        
        # nearest_points method (attaches anywhere on a line)
        # join_points = nearest_points(closest_line, geom)
        # joins.append(LineString(join_points))
        
        # snap method (only attaches to line endpoints)
        closest_point_on_line = snap(geom, closest_line, r*100)
        joins.append(LineString((geom, closest_point_on_line)))
    
    return joins