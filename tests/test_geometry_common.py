import unittest
import allfed_spatial.geometry.common as common
from shapely.geometry import Point, LineString, LinearRing, Polygon
from shapely.geometry.collection import GeometryCollection

class Test_closest(unittest.TestCase):

    # Error case
    def test_point_no_targets(self):
        geom = Point(0, 0)
        targets = []
        with self.assertRaises(ValueError):
            closest_geometry = common.closest(geom, targets, 1)

    # Point
    def test_point_one_target(self):
        geom = Point(0, 0)
        targets = [Point(1, 1)]
        closest_geometry = common.closest(geom, targets, 1)
        self.assertEqual(closest_geometry, Point(1, 1))

    def test_point_two_targets(self):
        geom = Point(0, 0)
        targets = [Point(1, 1), Point(2, 2)]
        closest_geometry = common.closest(geom, targets, 1)
        self.assertEqual(closest_geometry, Point(1, 1))

    def test_second_closest_point_two_targets(self):
        geom = Point(0, 0)
        targets = [Point(1, 1), Point(2, 2)]
        closest_geometry = common.closest(geom, targets, 2)
        self.assertEqual(closest_geometry, Point(2, 2))

    # LineString
    def test_line_one_target(self):
        geom = LineString([Point(0, 0), Point(0, 1)])
        targets = [Point(1, 1)]
        closest_geometry = common.closest(geom, targets, 1)
        self.assertEqual(closest_geometry, Point(1, 1))

    def test_line_two_targets(self):
        geom = LineString([Point(0, 0), Point(0, 1)])
        targets = [Point(1, 1), Point(2, 2)]
        closest_geometry = common.closest(geom, targets, 1)
        self.assertEqual(closest_geometry, Point(1, 1))

    def test_line_edge_two_targets(self):
        geom = LineString([Point(0, 0), Point(0, 10)])
        targets = [Point(1, 5), Point(2, 10)]
        closest_geometry = common.closest(geom, targets, 1)
        self.assertEqual(closest_geometry, Point(1, 5))

    def test_line_point_two_targets(self):
        geom = LineString([Point(0, 0), Point(0, 10)])
        targets = [Point(2, 5), Point(1, 10)]
        closest_geometry = common.closest(geom, targets, 1)
        self.assertEqual(closest_geometry, Point(1, 10))

    # LinearRing
    def test_linear_ring_one_target(self):
        geom = LinearRing([(0, 0), (0, 1), (1, 1), (1, 0)])
        targets = [Point(0.5, 0.5)]
        closest_geometry = common.closest(geom, targets, 1)
        self.assertEqual(closest_geometry, Point(0.5, 0.5))

    def test_linear_ring_inside_two_targets(self):
        geom = LinearRing([(0, 0), (0, 1), (1, 1), (1, 0)])
        targets = [Point(0.5, 0.5), Point(2, 2)]
        closest_geometry = common.closest(geom, targets, 1)
        self.assertEqual(closest_geometry, Point(0.5, 0.5))

    def test_linear_ring_outside_two_targets(self):
        geom = LinearRing([(0, 0), (0, 1), (1, 1), (1, 0)])
        targets = [Point(0.5, 0.5), Point(0.5, 1.4)]
        closest_geometry = common.closest(geom, targets, 1)
        self.assertEqual(closest_geometry, Point(0.5, 1.4))

    # Polygon
    def test_polygon_one_target(self):
        geom = Polygon([(0, 0), (0, 1), (1, 1), (1, 0)])
        targets = [Point(0.5, 0.5)]
        closest_geometry = common.closest(geom, targets, 1)
        self.assertEqual(closest_geometry, Point(0.5, 0.5))

    def test_polygon_two_targets(self):
        geom = Polygon([(0, 0), (0, 1), (1, 1), (1, 0)])
        targets = [Point(0.5, 0.5), Point(2, 2)]
        closest_geometry = common.closest(geom, targets, 1)
        self.assertEqual(closest_geometry, Point(0.5, 0.5))

    def test_polygon_inside_two_targets(self):
        geom = Polygon([(0, 0), (0, 1), (1, 1), (1, 0)])
        targets = [Point(0.5, 0.5), Point(2, 2)]
        closest_geometry = common.closest(geom, targets, 1)
        self.assertEqual(closest_geometry, Point(0.5, 0.5))

    # Polygons are filled, so the interior point is still closer
    def test_polygon_outside_two_targets(self):
        geom = Polygon([(0, 0), (0, 1), (1, 1), (1, 0)])
        targets = [Point(0.5, 0.5), Point(0.5, 1.4)]
        closest_geometry = common.closest(geom, targets, 1)
        self.assertEqual(closest_geometry, Point(0.5, 0.5))

    # Imagine a C like shape
    def test_polygon_cresent_two_targets(self):
        geom = Polygon([(1, 1.5), (1, 2), (0, 2), (0, 0), (1, 0), (1, 0.5), (1.1, 0.5), (1.1, -0.1), (-0.1, -0.1), (-0.1, 2.1), (1.1, 2.1), (1.1, 1.5)])
        targets = [Point(0.5, 1), Point(1.5, 0)]
        closest_geometry = common.closest(geom, targets, 1)
        self.assertEqual(closest_geometry, Point(1.5, 0))

    # If the polygon has a hole in the middle then an outside point can be closer again
    def test_polygon_with_hole_two_targets(self):
        geom = Polygon([(0, 0), (0, 1), (1, 1), (1, 0)], [LinearRing([(0.5, 0), (0, 0.5), (0.5, 1), (1, 0.5)])])
        targets = [Point(0.5, 0.5), Point(0.5, 1.2)]
        closest_geometry = common.closest(geom, targets, 1)
        self.assertEqual(closest_geometry, Point(0.5, 1.2))

    # Collections and other stuff - the number of combinations starts to explode here, so just checking some basics
    def test_collection_one_target(self):
        geom = GeometryCollection([Point(0, 0), LineString([(1, 0), (1, 1)])])
        targets = [Point(1, 1)]
        closest_geometry = common.closest(geom, targets, 1)
        self.assertEqual(closest_geometry, Point(1, 1))

    def test_collection_two_targets(self):
        geom = GeometryCollection([Point(0, 0), LineString([(1, 0), (1, 1)])])
        targets = [Point(0, 0.5), Point(1.4, 0.5)]
        closest_geometry = common.closest(geom, targets, 1)
        self.assertEqual(closest_geometry, Point(1.4, 0.5))

    def test_collection_two_line_targets(self):
        geom = GeometryCollection([Point(0, 0), LineString([(1, 0), (1, 1)])])
        targets = [LineString([(-0.5, 0), (0.5, 0)]), LineString([(1.1, 0), (1.1, 1)])]
        closest_geometry = common.closest(geom, targets, 1)
        self.assertEqual(closest_geometry, LineString([(-0.5, 0), (0.5, 0)]))

    def test_collection_two_mixed_targets(self):
        geom = GeometryCollection([Point(0, 0), LineString([(1, 0), (1, 1)])])
        targets = [Point(0.5, 0.5), LineString([(0, 2.1), (2, 0)])]
        closest_geometry = common.closest(geom, targets, 1)
        self.assertEqual(closest_geometry, LineString([(0, 2.1), (2, 0)]))

    # This just confirms an edge case, if this changes, this test can be updated
    def test_two_equal_targets(self):
        geom = LineString([(0, 0), (1, 1)])
        targets1 = [Point(0, 0), Point(1, 1)]
        closest_geometry1 = common.closest(geom, targets1, 1)
        targets2 = [Point(1, 1), Point(0, 0)]
        closest_geometry2 = common.closest(geom, targets2, 1)
        self.assertNotEqual(closest_geometry1, closest_geometry2)

class Test_closest_within_radius(unittest.TestCase):

    def test_point_within_radius(self):
        geom = Point(0, 0)
        targets = [Point(1, 1)]
        closest_geometry = common.closest_within_radius(geom, targets, 10, 1)
        self.assertEqual(closest_geometry, Point(1, 1))

    def test_point_outside_radius(self):
        geom = Point(0, 0)
        targets = [Point(100, 100)]
        closest_geometry = common.closest_within_radius(geom, targets, 10, 1)
        self.assertEqual(closest_geometry, None)

    def test_point_exactly_on_radius(self):
        geom = Point(0, 0)
        targets = [Point(10, 0)]
        closest_geometry = common.closest_within_radius(geom, targets, 10, 1)
        self.assertEqual(closest_geometry, Point(10, 0))
    
    def test_point_just_outside_radius(self):
        geom = Point(0, 0)
        targets = [Point(10, 0.000001)]
        closest_geometry = common.closest_within_radius(geom, targets, 10, 1)
        self.assertEqual(closest_geometry, None)

    # second closest
    def test_second_point_within_radius(self):
        geom = Point(0, 0)
        targets = [Point(0, 0), Point(1, 1)]
        closest_geometry = common.closest_within_radius(geom, targets, 10, 2)
        self.assertEqual(closest_geometry, Point(1, 1))

    def test_second_point_outside_radius(self):
        geom = Point(0, 0)
        targets = [Point(0, 0), Point(100, 100)]
        closest_geometry = common.closest_within_radius(geom, targets, 10, 2)
        self.assertEqual(closest_geometry, None)

    def test_second_point_exactly_on_radius(self):
        geom = Point(0, 0)
        targets = [Point(0, 0), Point(10, 0)]
        closest_geometry = common.closest_within_radius(geom, targets, 10, 2)
        self.assertEqual(closest_geometry, Point(10, 0))

    def test_second_point_just_outside_radius(self):
        geom = Point(0, 0)
        targets = [Point(0, 0), Point(10, 0.000001)]
        closest_geometry = common.closest_within_radius(geom, targets, 10, 2)
        self.assertEqual(closest_geometry, None)

    # error case
    def test_requesting_third_of_two_targets_throws(self):
        geom = Point(0, 0)
        targets = [Point(1, 1), Point(2, 2)]
        with self.assertRaises(ValueError):
            closest_geometry = common.closest_within_radius(geom, targets, 10, 3)

class Test_intersects(unittest.TestCase):

    def test_different_points_do_not_intersect(self):
        geom1 = Point(0, 0)
        geom2 = Point(1, 1)
        intersects = common.intersects(geom1, geom2)
        self.assertEqual(intersects, False)

    def test_same_points_do_intersect(self):
        geom1 = Point(0, 0)
        geom2 = Point(0, 0)
        intersects = common.intersects(geom1, geom2)
        self.assertEqual(intersects, True)

    def test_point_on_line_intersects(self):
        geom1 = Point(1, 1)
        geom2 = LineString([(0, 0), (2, 2)])
        intersects = common.intersects(geom1, geom2)
        self.assertEqual(intersects, True)

    def test_point_on_end_of_line_intersects(self):
        geom1 = Point(0, 0)
        geom2 = LineString([(0, 0), (2, 2)])
        intersects = common.intersects(geom1, geom2)
        self.assertEqual(intersects, True)

    def test_line_inside_linear_ring_does_not_intersect(self):
        geom1 = LineString([(1, 1), (3, 1)])
        geom2 = LinearRing([(4, 2), (0, 2), (0, 0), (4, 0)])
        intersects = common.intersects(geom1, geom2)
        self.assertEqual(intersects, False)

    def test_line_intersecting_linear_ring(self):
        geom1 = LineString([(1, 1), (3, 1)])
        geom2 = LinearRing([(2, 2), (0, 2), (0, 0), (2, 0)])
        intersects = common.intersects(geom1, geom2)
        self.assertEqual(intersects, True)

    def test_line_inside_polygon_intersects(self):
        geom1 = LineString([(1, 1), (3, 1)])
        geom2 = Polygon([(4, 2), (0, 2), (0, 0), (4, 0)])
        intersects = common.intersects(geom1, geom2)
        self.assertEqual(intersects, True)

    def test_line_on_polygon_edge_intersects(self):
        geom1 = LineString([(0, 0), (0, 2)])
        geom2 = Polygon([(4, 2), (0, 2), (0, 0), (4, 0)])
        intersects = common.intersects(geom1, geom2)
        self.assertEqual(intersects, True)

    def test_line_inside_collection_of_points_does_not_intersect(self):
        geom1 = LineString([(0.5, 0), (0.5, 1)])
        geom2 = GeometryCollection([Point(0, 0), Point(0, 1), Point(1, 0), Point(1, 1)])
        intersects = common.intersects(geom1, geom2)
        self.assertEqual(intersects, False)

    def test_line_inside_mixed_collection_does_intersect(self):
        geom1 = LineString([(0.5, 0), (0.5, 1)])
        geom2 = GeometryCollection([Point(0, 0), LinearRing([(0, 1), (1, 0), (1, 1)])])
        intersects = common.intersects(geom1, geom2)
        self.assertEqual(intersects, True)

class Test_closest_non_intersecting_within_radius(unittest.TestCase):

    def test_nearest_point_no_intersect(self):
        geom = Point(0, 0)
        non_intersect_geom = Point(1, 2)
        targets = [Point(1, 1), Point(2, 2)]
        closest = common.closest_non_intersecting_within_radius(geom, non_intersect_geom, targets, 10)
        self.assertEqual(closest, Point(1, 1))

    def test_nearest_point_after_intersect(self):
        geom = Point(0, 0)
        non_intersect_geom = Polygon([(0.5, 0.5), (0.5, 1.5), (1.5, 1.5), (1.5, 0.5)])
        targets = [Point(1, 1), Point(2, 2)]
        closest = common.closest_non_intersecting_within_radius(geom, non_intersect_geom, targets, 10)
        self.assertEqual(closest, Point(2, 2))

    def test_nearest_point_after_intersect_is_outside_radius(self):
        geom = Point(0, 0)
        non_intersect_geom = Point(1, 1)
        targets = [Point(1, 1), Point(20, 20)]
        closest = common.closest_non_intersecting_within_radius(geom, non_intersect_geom, targets, 10)
        self.assertEqual(closest, None)

    def test_second_nearest_point_including_intersect(self):
        geom = Point(0, 0)
        non_intersect_geom = Point(2, 2)
        targets = [Point(1, 1), Point(2, 2), Point(3, 3)]
        closest = common.closest_non_intersecting_within_radius(geom, non_intersect_geom, targets, 10, n=2)
        self.assertEqual(closest, Point(3, 3))

    def test_nearest_point_all_intersect(self):
        geom = Point(0, 0)
        non_intersect_geom = Polygon([(0.5, 0.5), (0.5, 2.5), (2.5, 2.5), (2.5, 0.5)])
        targets = [Point(1, 1), Point(2, 2)]
        closest = common.closest_non_intersecting_within_radius(geom, non_intersect_geom, targets, 10)
        self.assertEqual(closest, None)

    #    %%%%%%%   
    #    %     %   
    # X  %  A  %  B
    #    %     %   
    #    %%%%%%%   
    # consider the above situation:
    # - given point X as the geometry
    # - with '%' representing non-intersect geometry (a linear ring in this case)
    # - which point is closer A or B
    # if we just care about shortest distance,
    # then A is the closest
    # if we want the nearest where we can draw a line that doesn't intersect any of the non-intersect geometry,
    # then B is the closest
    def test_nearest_point_closest_through_geom(self):
        geom = Point(0, 0)
        non_intersect_geom = LinearRing([(0.5, 0.5), (0.5, 1.5), (1.5, 1.5), (1.5, 0.5)])
        targets = [Point(1, 1), Point(2, 2)]
        closest = common.closest_non_intersecting_within_radius(geom, non_intersect_geom, targets, 10)
        self.assertEqual(closest, Point(1, 1))

    # error case
    def test_requesting_third_of_two_non_intersecting_targets_throws(self):
        geom = Point(0, 0)
        non_intersect_geom = Point(1, 1)
        targets = [Point(1, 1), Point(2, 2), Point(3, 3)]
        with self.assertRaises(ValueError):
            closest = common.closest_non_intersecting_within_radius(geom, non_intersect_geom, targets, 10, n=3)

if __name__ == '__main__':
    unittest.main()