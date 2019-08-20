import unittest
import allfed_spatial.geometry.common as common
from shapely.geometry import Point, LineString, LinearRing, Polygon
from shapely.geometry.collection import GeometryCollection

class TestCommon(unittest.TestCase):

    # Error case
    def test_closest_point_no_targets(self):
        geom = Point(0, 0)
        targets = []
        failed = True
        with self.assertRaises(ValueError):
            closest_geometry = common.closest(geom, targets, 1)
            failed = false
        self.assertTrue(failed, "Expected an Error to be thrown")

# Point
    def test_closest_point_one_target(self):
        geom = Point(0, 0)
        targets = [Point(1, 1)]
        closest_geometry = common.closest(geom, targets, 1)
        self.assertEqual(closest_geometry, Point(1, 1))

    def test_closest_point_two_targets(self):
        geom = Point(0, 0)
        targets = [Point(1, 1), Point(2, 2)]
        closest_geometry = common.closest(geom, targets, 1)
        self.assertEqual(closest_geometry, Point(1, 1))

    def test_second_closest_point_two_targets(self):
        geom = Point(0, 0)
        targets = [Point(1, 1), Point(2, 2)]
        closest_geometry = common.closest(geom, targets, 2)
        self.assertEqual(closest_geometry, Point(2, 2))

#LineString
    def test_closest_line_one_target(self):
        geom = LineString([Point(0, 0), Point(0, 1)])
        targets = [Point(1, 1)]
        closest_geometry = common.closest(geom, targets, 1)
        self.assertEqual(closest_geometry, Point(1, 1))

    def test_closest_line_two_targets(self):
        geom = LineString([Point(0, 0), Point(0, 1)])
        targets = [Point(1, 1), Point(2, 2)]
        closest_geometry = common.closest(geom, targets, 1)
        self.assertEqual(closest_geometry, Point(1, 1))

    def test_closest_line_edge_two_targets(self):
        geom = LineString([Point(0, 0), Point(0, 10)])
        targets = [Point(1, 5), Point(2, 10)]
        closest_geometry = common.closest(geom, targets, 1)
        self.assertEqual(closest_geometry, Point(1, 5))

    def test_closest_line_point_two_targets(self):
        geom = LineString([Point(0, 0), Point(0, 10)])
        targets = [Point(2, 5), Point(1, 10)]
        closest_geometry = common.closest(geom, targets, 1)
        self.assertEqual(closest_geometry, Point(1, 10))

#LinearRing
    def test_closest_linear_ring_one_target(self):
        geom = LinearRing([(0, 0), (0, 1), (1, 1), (1, 0)])
        targets = [Point(0.5, 0.5)]
        closest_geometry = common.closest(geom, targets, 1)
        self.assertEqual(closest_geometry, Point(0.5, 0.5))

    def test_closest_linear_ring_inside_two_targets(self):
        geom = LinearRing([(0, 0), (0, 1), (1, 1), (1, 0)])
        targets = [Point(0.5, 0.5), Point(2, 2)]
        closest_geometry = common.closest(geom, targets, 1)
        self.assertEqual(closest_geometry, Point(0.5, 0.5))

    def test_closest_linear_ring_outside_two_targets(self):
        geom = LinearRing([(0, 0), (0, 1), (1, 1), (1, 0)])
        targets = [Point(0.5, 0.5), Point(0.5, 1.4)]
        closest_geometry = common.closest(geom, targets, 1)
        self.assertEqual(closest_geometry, Point(0.5, 1.4))

#Polygon
    def test_closest_polygon_one_target(self):
        geom = Polygon([(0, 0), (0, 1), (1, 1), (1, 0)])
        targets = [Point(0.5, 0.5)]
        closest_geometry = common.closest(geom, targets, 1)
        self.assertEqual(closest_geometry, Point(0.5, 0.5))

    def test_closest_polygon_two_targets(self):
        geom = Polygon([(0, 0), (0, 1), (1, 1), (1, 0)])
        targets = [Point(0.5, 0.5), Point(2, 2)]
        closest_geometry = common.closest(geom, targets, 1)
        self.assertEqual(closest_geometry, Point(0.5, 0.5))

    def test_closest_polygon_inside_two_targets(self):
        geom = Polygon([(0, 0), (0, 1), (1, 1), (1, 0)])
        targets = [Point(0.5, 0.5), Point(2, 2)]
        closest_geometry = common.closest(geom, targets, 1)
        self.assertEqual(closest_geometry, Point(0.5, 0.5))

    # Polygons are filled, so the interior point is still closer
    def test_closest_polygon_outside_two_targets(self):
        geom = Polygon([(0, 0), (0, 1), (1, 1), (1, 0)])
        targets = [Point(0.5, 0.5), Point(0.5, 1.4)]
        closest_geometry = common.closest(geom, targets, 1)
        self.assertEqual(closest_geometry, Point(0.5, 0.5))

    # Imagine a C like shape
    def test_closest_polygon_cresent_two_targets(self):
        geom = Polygon([(1, 1.5), (1, 2), (0, 2), (0, 0), (1, 0), (1, 0.5), (1.1, 0.5), (1.1, -0.1), (-0.1, -0.1), (-0.1, 2.1), (1.1, 2.1), (1.1, 1.5)])
        targets = [Point(0.5, 1), Point(1.5, 0)]
        closest_geometry = common.closest(geom, targets, 1)
        self.assertEqual(closest_geometry, Point(1.5, 0))

    # If the polygon has a hole in the middle then an outside point can be closer again
    def test_closest_polygon_with_hole_two_targets(self):
        geom = Polygon([(0, 0), (0, 1), (1, 1), (1, 0)], [LinearRing([(0.5, 0), (0, 0.5), (0.5, 1), (1, 0.5)])])
        targets = [Point(0.5, 0.5), Point(0.5, 1.2)]
        closest_geometry = common.closest(geom, targets, 1)
        self.assertEqual(closest_geometry, Point(0.5, 1.2))

#Collections and other stuff - the number of combinations starts to explode here, so just checking some basics
    def test_closest_collection_one_target(self):
        geom = GeometryCollection([Point(0, 0), LineString([(1, 0), (1, 1)])])
        targets = [Point(1, 1)]
        closest_geometry = common.closest(geom, targets, 1)
        self.assertEqual(closest_geometry, Point(1, 1))

    def test_closest_collection_two_targets(self):
        geom = GeometryCollection([Point(0, 0), LineString([(1, 0), (1, 1)])])
        targets = [Point(0, 0.5), Point(1.4, 0.5)]
        closest_geometry = common.closest(geom, targets, 1)
        self.assertEqual(closest_geometry, Point(1.4, 0.5))

    def test_closest_collection_two_line_targets(self):
        geom = GeometryCollection([Point(0, 0), LineString([(1, 0), (1, 1)])])
        targets = [LineString([(-0.5, 0), (0.5, 0)]), LineString([(1.1, 0), (1.1, 1)])]
        closest_geometry = common.closest(geom, targets, 1)
        self.assertEqual(closest_geometry, LineString([(-0.5, 0), (0.5, 0)]))

    def test_closest_collection_two_mixed_targets(self):
        geom = GeometryCollection([Point(0, 0), LineString([(1, 0), (1, 1)])])
        targets = [Point(0.5, 0.5), LineString([(0, 2.1), (2, 0)])]
        closest_geometry = common.closest(geom, targets, 1)
        self.assertEqual(closest_geometry, LineString([(0, 2.1), (2, 0)]))

    # This just confirms an edge case, if this changes, this test can be updated
    def test_closest_two_equal_targets(self):
        geom = LineString([(0, 0), (1, 1)])
        targets1 = [Point(0, 0), Point(1, 1)]
        closest_geometry1 = common.closest(geom, targets1, 1)
        targets2 = [Point(1, 1), Point(0, 0)]
        closest_geometry2 = common.closest(geom, targets2, 1)
        self.assertNotEqual(closest_geometry1, closest_geometry2)

if __name__ == '__main__':
    unittest.main()