import unittest
import allfed_spatial.geometry.line as geometry_line
from shapely.geometry import Point, LineString, MultiLineString

class TestLine(unittest.TestCase):

# make_points_on_line
    def test_make_points_on_line_not_a_line(self):
        line = Point(0, 0)
        distance = 1.5
        failed = True
        with self.assertRaises(ValueError):
            points = geometry_line.make_points_on_line(line, distance)
            failed = False
        self.assertTrue(failed, "Expected an Error to be thrown")

    def test_make_points_on_line_large_dist(self):
        line = LineString([Point(0, 0), Point(0, 1)])
        distance = 1.5
        points = geometry_line.make_points_on_line(line, distance)
        self.assertEqual(points, [Point(0, 0.5)])

    def test_make_points_on_line_small_dist(self):
        line = LineString([Point(0, 0), Point(0, 1)])
        distance = 0.3
        points = geometry_line.make_points_on_line(line, distance)
        self.assertEqual(points, [Point(0, 0.25), Point(0, 0.5), Point(0, 0.75)])

    def test_make_points_on_line_edge_dist(self):
        line = LineString([Point(0, 0), Point(0, 1)])
        distance = 0.5
        points = geometry_line.make_points_on_line(line, distance)
        self.assertEqual(points, [Point(0, 0.5)])

    def test_make_points_on_line_small_edge_dist(self):
        line = LineString([Point(0, 0), Point(0, 1)])
        distance = 0.2
        points = geometry_line.make_points_on_line(line, distance)
        self.assertEqual(points, [Point(0, 0.2), Point(0, 0.4), Point(0, 0.6), Point(0, 0.8)])

if __name__ == '__main__':
    unittest.main()