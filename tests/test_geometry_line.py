import unittest
import allfed_spatial.geometry.line as geometry_line
from shapely.geometry import Point, LineString, MultiLineString

class Test_make_points_on_line(unittest.TestCase):

    def PointsEqual(self, points1, points2):
        if (points1 == None or points2 == None):
            self.fail("provided None as points")
        self.assertEqual(len(points1), len(points2))
        for idx in range(len(points1)):
            self.assertAlmostEqual(points1[idx].distance(points2[idx]), 0, delta=0.000001, msg="points are different")

    def test_not_a_line(self):
        line = Point(0, 0)
        distance = 1.5
        with self.assertRaises(ValueError):
            points = geometry_line.make_points_on_line(line, distance)

    def test_large_dist(self):
        line = LineString([Point(0, 0), Point(0, 1)])
        distance = 1.5
        points = geometry_line.make_points_on_line(line, distance)
        self.PointsEqual(points, [Point(0, 0.5)])

    def test_small_dist(self):
        line = LineString([Point(0, 0), Point(0, 1)])
        distance = 0.3
        points = geometry_line.make_points_on_line(line, distance)
        self.PointsEqual(points, [Point(0, 0.25), Point(0, 0.5), Point(0, 0.75)])

    def test_edge_dist(self):
        line = LineString([Point(0, 0), Point(0, 1)])
        distance = 0.5
        points = geometry_line.make_points_on_line(line, distance)
        self.PointsEqual(points, [Point(0, 0.5)])

    def test_small_edge_dist(self):
        line = LineString([Point(0, 0), Point(0, 1)])
        distance = 0.2
        points = geometry_line.make_points_on_line(line, distance)
        self.PointsEqual(points, [Point(0, 0.2), Point(0, 0.4), Point(0, 0.6), Point(0, 0.8)])

    def test_multi_point_line_large_dist(self):
        line = LineString([Point(0, 0), Point(0, 1), Point(1, 1)])
        distance = 2.5
        points = geometry_line.make_points_on_line(line, distance)
        self.PointsEqual(points, [Point(0, 1)])

    def test_multi_point_line_small_dist(self):
        line = LineString([Point(0, 0), Point(0, 1), Point(1, 1)])
        distance = 0.6
        points = geometry_line.make_points_on_line(line, distance)
        self.PointsEqual(points, [Point(0, 0.5), Point(0, 1), Point(0.5, 1)])

    def test_multi_point_line_edge_dist(self):
        line = LineString([Point(0, 0), Point(0, 1), Point(1, 1)])
        distance = 1
        points = geometry_line.make_points_on_line(line, distance)
        self.PointsEqual(points, [Point(0, 1)])

    def test_multi_point_line_small_edge_dist(self):
        line = LineString([Point(0, 0), Point(0, 1), Point(1, 1)])
        distance = 0.4
        points = geometry_line.make_points_on_line(line, distance)
        self.PointsEqual(points, [Point(0, 0.4), Point(0, 0.8), Point(0.2, 1), Point(0.6, 1)])

    def test_multi_line_large_dist(self):
        line = MultiLineString([LineString([Point(0, 0), Point(0, 1)]), LineString([Point(1, 0), Point(1, 1)])])
        distance = 0.8
        points = geometry_line.make_points_on_line(line, distance)
        self.PointsEqual(points, [Point(0, 0.5), Point(1, 0.5)])

    def test_multi_line_small_dist(self):
        line = MultiLineString([LineString([Point(0, 0), Point(0, 1)]), LineString([Point(1, 0), Point(1, 1)])])
        distance = 0.3
        points = geometry_line.make_points_on_line(line, distance)
        self.PointsEqual(points, [Point(0, 0.25), Point(0, 0.5), Point(0, 0.75), Point(1, 0.25), Point(1, 0.5), Point(1, 0.75)])

    def test_multi_line_edge_dist(self):
        line = MultiLineString([LineString([Point(0, 0), Point(0, 1)]), LineString([Point(1, 0), Point(1, 1)])])
        distance = 0.5
        points = geometry_line.make_points_on_line(line, distance)
        self.PointsEqual(points, [Point(0, 0.5), Point(1, 0.5)])

    def test_multi_line_small_edge_dist(self):
        line = MultiLineString([LineString([Point(0, 0), Point(0, 1)]), LineString([Point(1, 0), Point(1, 1)])])
        distance = 0.2
        points = geometry_line.make_points_on_line(line, distance)
        self.PointsEqual(points, [Point(0, 0.2), Point(0, 0.4), Point(0, 0.6), Point(0, 0.8), Point(1, 0.2), Point(1, 0.4), Point(1, 0.6), Point(1, 0.8)])

if __name__ == '__main__':
    unittest.main()