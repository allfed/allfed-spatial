import unittest
import allfed_spatial.geometry.line as geometry_line
from shapely.geometry import Point, LineString, MultiLineString

class LineBaseTest(unittest.TestCase):

    def PointEqual(self, p1, p2, diff=0.000001):
        self.assertAlmostEqual(
            p1.distance(p2),
            0,
            delta=diff,
            msg="points are different")

    def PointsEqual(self, points1, points2):
        if (points1 == None or points2 == None):
            self.fail("provided None as points")
        self.assertEqual(
            len(points1),
            len(points2),
            msg="different number of points")
        for idx in range(len(points1)):
            self.PointEqual(points1[idx], points2[idx])

    def LinesEquivalent(self, lines1, lines2):
        if (lines1 == None or lines2 == None):
            self.fail("provided None as lines")
        self.assertEqual(
            len(lines1),
            len(lines2),
            msg="different number of lines")
        for idx in range(len(lines1)):
            dist1 = lines1[idx].length
            dist2 = lines2[idx].length
            diff = dist1/dist2
            self.assertAlmostEqual(
                diff,
                1,
                delta=0.0105,
                msg="lines are more than 1.05 percent different length")

            distDiff = abs(dist1 - dist2) * 1.05
            self.PointEqual(
                Point(list(lines1[idx].coords)[0]),
                Point(list(lines2[idx].coords)[0]),
                diff=distDiff)
            self.PointEqual(
                Point(list(lines1[idx].coords)[-1]),
                Point(list(lines2[idx].coords)[-1]),
                diff=distDiff)

            f_distance = geometry_line.frechet_distance(
                [Point(p) for p in lines1[idx].coords],
                [Point(p) for p in lines2[idx].coords])
            self.assertLess(
                f_distance,
                distDiff,
                "line internal shape is significantly different")

class Test_frechet_distance(LineBaseTest):
    def test_lines_equivalent(self):
        points1 = [
            Point(0, 0),
            Point(0, 0.5),
            Point(0.5, 0.5),
            Point(1, 0.5),
            Point(1, 1)
        ]
        points2 = [
            Point(0, 0),
            Point(0, 0.5),
            Point(1, 0.5),
            Point(1, 1)
        ]
        distance = geometry_line.frechet_distance(points1, points2)
        self.assertLess(
            distance,
            0.01,
            "Expected lines to be effectively equal")

    def test_lines_not_equivalent(self):
        points1 = [
            Point(0, 0),
            Point(0, 0.5),
            Point(0.5, 0.5),
            Point(1, 0.5),
            Point(1, 1)
        ]
        points2 = [
            Point(0, 0),
            Point(0, 0.5),
            Point(0.5, 1),
            Point(1, 1)
        ]
        distance = geometry_line.frechet_distance(points1, points2)
        self.assertLess(
            distance,
            0.67,
            "Distance approximation is getting too high to be useful, " +
            "expected ~0.66")
        self.assertGreaterEqual(
            distance,
            0.5,
            "Expected distance to be at least 0.5 (the minimum distance)")

    def test_longer_lines(self):
        points1 = [
            Point(1, 0),
            Point(1, 1),
            Point(1, 2),
            Point(1, 3),
            Point(1, 4),
            Point(3, 4),
            Point(3, 6),
            Point(1, 6),
            Point(1, 7)
        ]
        points2 = [
            Point(0, 0),
            Point(0, -2),
            Point(2, -2),
            Point(0, 2),
            Point(0, 7)
        ]
        distance = geometry_line.frechet_distance(points1, points2)
        self.assertLess(
            distance,
            6.09,
            "Distance approximation is getting too high to be useful, " +
            "expected ~6.08")
        self.assertGreaterEqual(
            distance,
            3,
            "Expected distance to be at least 3 (the minimum distance)")

class Test_make_points_on_line(LineBaseTest):

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
        self.PointsEqual(
            points,
            [Point(0, 0.25), Point(0, 0.5), Point(0, 0.75)])

    def test_edge_dist(self):
        line = LineString([Point(0, 0), Point(0, 1)])
        distance = 0.5
        points = geometry_line.make_points_on_line(line, distance)
        self.PointsEqual(points, [Point(0, 0.5)])

    def test_small_edge_dist(self):
        line = LineString([Point(0, 0), Point(0, 1)])
        distance = 0.2
        points = geometry_line.make_points_on_line(line, distance)
        self.PointsEqual(
            points,
            [Point(0, 0.2), Point(0, 0.4), Point(0, 0.6), Point(0, 0.8)])

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
        self.PointsEqual(
            points,
            [Point(0, 0.4), Point(0, 0.8), Point(0.2, 1), Point(0.6, 1)])

    def test_multi_line_large_dist(self):
        line = MultiLineString([
            LineString([Point(0, 0), Point(0, 1)]),
            LineString([Point(1, 0), Point(1, 1)])
        ])
        distance = 0.8
        points = geometry_line.make_points_on_line(line, distance)
        self.PointsEqual(points, [Point(0, 0.5), Point(1, 0.5)])

    def test_multi_line_small_dist(self):
        line = MultiLineString([
            LineString([Point(0, 0), Point(0, 1)]),
            LineString([Point(1, 0), Point(1, 1)])
        ])
        distance = 0.3
        points = geometry_line.make_points_on_line(line, distance)
        self.PointsEqual(
            points,
            [
                Point(0, 0.25),
                Point(0, 0.5),
                Point(0, 0.75),
                Point(1, 0.25),
                Point(1, 0.5),
                Point(1, 0.75)
            ])

    def test_multi_line_edge_dist(self):
        line = MultiLineString([
            LineString([Point(0, 0), Point(0, 1)]),
            LineString([Point(1, 0), Point(1, 1)])
        ])
        distance = 0.5
        points = geometry_line.make_points_on_line(line, distance)
        self.PointsEqual(points, [Point(0, 0.5), Point(1, 0.5)])

    def test_multi_line_small_edge_dist(self):
        line = MultiLineString([
            LineString([Point(0, 0), Point(0, 1)]),
            LineString([Point(1, 0), Point(1, 1)])
        ])
        distance = 0.2
        points = geometry_line.make_points_on_line(line, distance)
        self.PointsEqual(
            points,
            [
                Point(0, 0.2),
                Point(0, 0.4),
                Point(0, 0.6),
                Point(0, 0.8),
                Point(1, 0.2),
                Point(1, 0.4),
                Point(1, 0.6),
                Point(1, 0.8)
            ])

class Test_split_line_by_distance(LineBaseTest):
    def test_halve_a_line(self):
        line = LineString([Point(0, 0), Point(0, 1)])
        distance = 0.5
        splitLines = geometry_line.split_line_by_distance(line, distance)
        self.LinesEquivalent(
            splitLines,
            [LineString([(0, 0), (0, 0.5)]), LineString([(0, 0.5), (0, 1)])])

class Test_split_features_by_distance(LineBaseTest):
    pass

class Test_join_points_to_lines(LineBaseTest):
    pass


if __name__ == '__main__':
    unittest.main()