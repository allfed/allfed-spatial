import unittest
import allfed_spatial.geometry.line as geometry_line
from shapely.geometry import Point, LineString, MultiLineString
from allfed_spatial.features.feature import Feature

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

    def LineEquivalent(self, line1, line2):
        dist1 = line1.length
        dist2 = line2.length
        if (dist2 != 0):
            ratio = dist1/dist2
        elif (dist1 == 0):
            ratio = 1
        else:
            ratio = float("inf")
        self.assertAlmostEqual(
            ratio,
            1,
            delta=0.02,
            msg="lines are more than 2 percent different length")

        distance_diff = max(max(dist1, dist2) * 0.015, 0.000001)

        self.PointEqual(
            Point(list(line1.coords)[0]),
            Point(list(line2.coords)[0]),
            diff=distance_diff)
        self.PointEqual(
            Point(list(line1.coords)[-1]),
            Point(list(line2.coords)[-1]),
            diff=distance_diff)

        f_distance = geometry_line.frechet_distance(
            [Point(p) for p in line1.coords],
            [Point(p) for p in line2.coords])
        self.assertLess(
            f_distance,
            distance_diff,
            "line is significantly different")

    def LinesEquivalent(self, lines1, lines2):
        if (lines1 == None or lines2 == None):
            self.fail("provided None as lines")
        self.assertEqual(
            len(lines1),
            len(lines2),
            msg="different number of lines")
        for idx in range(len(lines1)):
            self.LineEquivalent(lines1[idx], lines2[idx])

    def FeaturesEqual(self, features1, features2):
        if (features1 == None or features2 == None):
            self.fail("provided None as features")

        self.assertEqual(
            len(features1),
            len(features2),
            msg="different number of features")

        for idx in range(len(features1)):
            self.LineEquivalent(features1[idx].geom, features2[idx].geom)
            self.assertEqual(
                features1[idx].data,
                features2[idx].data,
                "feature data is different")

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
            "Distance approximation is too high to be useful, expected ~0.66")
        self.assertGreaterEqual(
            distance,
            0.5,
            "Expected distance to be at least 0.5 (minimum possible distance)")

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
            5.37,
            "Distance approximation is too high to be useful, expected ~5.36")
        self.assertGreaterEqual(
            distance,
            3,
            "Expected distance to be at least 3 (minimum possible distance)")

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
            [
                LineString([(0, 0), (0, 0.5)]),
                LineString([(0, 0.5), (0, 1)])
            ])

    def test_more_than_halve_a_line(self):
        line = LineString([Point(0, 0), Point(0, 1)])
        distance = 0.4
        splitLines = geometry_line.split_line_by_distance(line, distance)
        self.LinesEquivalent(
            splitLines,
            [
                LineString([(0, 0), (0, 0.333)]),
                LineString([(0, 0.333), (0, 0.666)]),
                LineString([(0, 0.666), (0, 1)])
            ])

    def test_less_than_halve_a_line(self):
        line = LineString([Point(0, 0), Point(0, 1)])
        distance = 0.7
        splitLines = geometry_line.split_line_by_distance(line, distance)
        self.LinesEquivalent(
            splitLines,
            [
                LineString([(0, 0), (0, 0.5)]),
                LineString([(0, 0.5), (0, 1)])
            ])

    def test_halve_a_multi_point_line(self):
        line = LineString([Point(0, 0), Point(0, 1), Point(1, 1)])
        distance = 1
        splitLines = geometry_line.split_line_by_distance(line, distance)
        self.LinesEquivalent(
            splitLines,
            [
                LineString([(0, 0), (0, 1)]),
                LineString([(0, 1), (1, 1)])
            ])

    def test_more_than_halve_a_multi_point_line(self):
        line = LineString([Point(0, 0), Point(0, 1), Point(1, 1)])
        distance = 0.8
        splitLines = geometry_line.split_line_by_distance(line, distance)
        self.LinesEquivalent(
            splitLines,
            [
                LineString([(0, 0), (0, 0.666)]),
                LineString([(0, 0.666), (0, 1), (0.333, 1)]),
                LineString([(0.333, 1), (1, 1)])
            ])

    def test_less_than_halve_a_multi_point_line(self):
        line = LineString([Point(0, 0), Point(0, 1), Point(1, 1)])
        distance = 1.4
        splitLines = geometry_line.split_line_by_distance(line, distance)
        self.LinesEquivalent(
            splitLines,
            [
                LineString([(0, 0), (0, 1)]),
                LineString([(0, 1), (1, 1)])
            ])

class Test_split_features_by_distance(LineBaseTest):
    def test_empty_list(self):
        features = []
        distance = 1
        result = geometry_line.split_features_by_distance(features, distance)
        self.FeaturesEqual(result, [])

    def test_no_split(self):
        test_data = {"this":"is", "a":"test", "testing":123}
        test_line = LineString([(0, 0), (0, 1)])
        features = [Feature(test_line, test_data)]
        distance = 2
        result = geometry_line.split_features_by_distance(features, distance)
        self.FeaturesEqual(result, [Feature(test_line, test_data)])

    def test_split_in_half(self):
        test_data = {"this":"is", "a":"test", "testing":123}
        test_line = LineString([(0, 0), (0, 1)])
        features = [Feature(test_line, test_data)]
        distance = 0.5
        result = geometry_line.split_features_by_distance(features, distance)
        self.FeaturesEqual(result, [
            Feature(LineString([(0, 0), (0, 0.5)]), test_data),
            Feature(LineString([(0, 0.5), (0, 1)]), test_data)
        ])

    def test_split_multiple_features(self):
        test_data1 = {"this":"is", "a":"test", "testing":123}
        test_line1 = LineString([(0, 0), (0, 1)])
        test_data2 = {"thiss":"is", "another":"test", "testing":1234}
        test_line2 = LineString([(0, 1), (0, 1.5)])
        test_data3 = {"thisss":"is", "yet another":"test", "testing":1235}
        test_line3 = LineString([(0, 1.5), (0, 3.75)])
        features = [
            Feature(test_line1, test_data1),
            Feature(test_line2, test_data2),
            Feature(test_line3, test_data3),
        ]
        distance = 0.75
        result = geometry_line.split_features_by_distance(features, distance)
        self.FeaturesEqual(result, [
            Feature(LineString([(0, 0), (0, 0.5)]), test_data1),
            Feature(LineString([(0, 0.5), (0, 1)]), test_data1),
            Feature(LineString([(0, 1), (0, 1.5)]), test_data2),
            Feature(LineString([(0, 1.5), (0, 2.25)]), test_data3),
            Feature(LineString([(0, 2.25), (0, 3)]), test_data3),
            Feature(LineString([(0, 3), (0, 3.75)]), test_data3)
        ])

class Test_join_points_to_lines(LineBaseTest):
    def test_no_points_no_lines(self):
        points = []
        lines = []
        result = geometry_line.join_points_to_lines(points, lines)
        self.PointsEqual(result, [])

    def test_no_points_one_line(self):
        points = []
        lines = [LineString([(0, 0), (0, 1)])]
        result = geometry_line.join_points_to_lines(points, lines)
        self.PointsEqual(result, [])

    def test_one_point_one_line(self):
        points = [Point(1, 0.5)]
        lines = [LineString([(0, 0), (0, 2)])]
        result = geometry_line.join_points_to_lines(points, lines)
        self.LinesEquivalent(result, [
            LineString([(1, 0.5), (0, 0)])
        ])

    def test_one_point_two_lines_prioritizes_points(self):
        points = [Point(1, 0.5)]
        lines = [LineString([(0, 0), (0, 2)]), LineString([(1, -1), (1, 2)])]
        result = geometry_line.join_points_to_lines(points, lines)
        self.LinesEquivalent(result, [
            LineString([(1, 0.5), (0, 0)])
        ])

    def test_multiple_points_multiple_lines(self):
        points = [
            Point(0, 1.5),
            Point(1, -1.5),
            Point(0.5, -2), # checking interior points
            Point(2.5, 0.5),
            Point(0, -4),
            Point(0, -4), # checking duplicates
        ]
        lines = [
            LineString([(0, 0), (0, 2)]),
            LineString([(1, -1), (1, 2)]),
            LineString([(0, 0), (0, -2), (0, -4)]),
            LineString([(1, 0), (2, 0)]),
        ]
        result = geometry_line.join_points_to_lines(points, lines)
        self.LinesEquivalent(result, [
            LineString([(0, 1.5), (0, 2)]),
            LineString([(1, -1.5), (1, -1)]),
            LineString([(0.5, -2), (1, -1)]), # interior points aren't used
            LineString([(2.5, 0.5), (2, 0)]),
            LineString([(0, -4), (0, -4)]),
            LineString([(0, -4), (0, -4)]), # duplicates are fine
        ])

if __name__ == '__main__':
    unittest.main()