
def find_closest(geom, targets):
    closest = (None, 10000000)
    for t in targets:
        dist = geom.distance(t)
        if dist < closest[1]:
            closest = (t, dist)
    return closest