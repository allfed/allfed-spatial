import rtree
import copy
from shapely.ops import snap


def snap_linestrings(r, lines):
    """ Geometrically 'snaps' LineStrings within an array together
    within a tolerance.
    
    Arguments:
        r {int|float} -- Tolerance radius in metres within which to snap lines 
                   together
        lines {list} -- Array of Shapely LineStrings
    
    Returns:
        array -- Array of snapped Shapely LineStrings
    """

    # create an empty spatial index object
    index = rtree.index.Index()
    
    snapped = []
    
    # populate the spatial index
    for index_id, geom in enumerate(lines):
        index.insert(index_id, geom.bounds)
    
    # create snapped lines
    for search_id, geom in enumerate(lines):
        
        # buffer the line
        buffered = geom.buffer(r)

        # get list of fids where bounding boxes intersect
        index_ids = [int(i) for i in index.intersection(buffered.bounds)]

        # access the features that those fids reference
        new_geom = copy.deepcopy(geom)
        for index_id in index_ids:
            
            if search_id == index_id:
                continue
            
            new_geom = snap(new_geom, lines[index_id], r)
            
            index.delete(search_id, geom.bounds)
        
        snapped.append(new_geom)
    
    return snapped