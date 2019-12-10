import unittest
from shapely.ops import linemerge
from shapely.geometry import LineString
import allfed_spatial.geometry.merge as geometry_merge
from allfed_spatial.features.feature import Feature
from tests.test_geometry_line import LineBaseTest

class Test_linemerge(LineBaseTest):
    """ Confirm the usage of linemerge """

    def test_2_connected_lines(self):
        line1 = LineString([(0, 0), (1, 1)])
        line2 = LineString([(1, 1), (2, 2)])
        result = linemerge([line1, line2])
        self.assertEqual(result.geom_type, 'LineString')
        self.LineEquivalent(
            result,
            LineString([(0, 0), (1, 1), (2, 2)]))

    def test_3_connected_lines(self):
        line1 = LineString([(0, 0), (1, 1)])
        line2 = LineString([(1, 1), (2, 2)])
        line3 = LineString([(2, 2), (3, 3)])
        result = linemerge([line1, line2, line3])
        self.assertEqual(result.geom_type, 'LineString')
        self.LineEquivalent(
            result,
            LineString([(0, 0), (1, 1), (2, 2), (3, 3)]))

    def test_2_disconnected_lines(self):
        line1 = LineString([(0, 0), (1, 1)])
        line2 = LineString([(1, 1.000001), (2, 2)])
        result = linemerge([line1, line2])
        self.assertEqual(result.geom_type, 'MultiLineString')
        self.LinesEquivalent(
            result,
            [
                LineString([(0, 0), (1, 1)]),
                LineString([(1, 1.000001), (2, 2)])
            ])

    def test_disconnect_and_connect_lines(self):
        line1 = LineString([(0, 0), (1, 1)])
        line2 = LineString([(1, 1.000001), (2, 2)])
        line3 = LineString([(2, 2), (3, 3)])
        result = linemerge([line1, line2, line3])
        self.assertEqual(result.geom_type, 'MultiLineString')
        self.LinesEquivalent(
            result,
            [
                LineString([(0, 0), (1, 1)]),
                LineString([(1, 1.000001), (2, 2), (3, 3)])
            ])

class Test_merge_features(LineBaseTest):
    def test_no_features(self):
        with self.assertRaises(ValueError):
            geometry_merge.merge_features([])

    def test_one_feature(self):
        feature1 = Feature(
            LineString([(0, 0), (1, 1)]),
            {'feature': 1, 'test 1': 'data 23'})
        result = geometry_merge.merge_features([feature1])
        self.FeaturesEqual(result, [feature1])

    def test_two_features_merge(self):
        f1data = {'feature': 1, 'test 1': 'data 23'}
        f2data = {'feature': 2, 'test 2': 'data 34'}
        feature1 = Feature(LineString([(0, 0), (1, 1)]), f1data)
        feature2 = Feature(LineString([(1, 1), (2, 2)]), f2data)
        result = geometry_merge.merge_features([feature1, feature2])
        self.FeaturesEqual(result, [
            Feature(LineString([(0, 0), (1, 1), (2, 2)]), f1data)
        ])

    def test_two_features_dont_merge(self):
        f1data = {'feature': 1, 'test 1': 'data 23'}
        f2data = {'feature': 2, 'test 2': 'data 34'}
        feature1 = Feature(LineString([(0, 0), (1, 1)]), f1data)
        feature2 = Feature(LineString([(1, 1.000001), (2, 2)]), f2data)
        result = geometry_merge.merge_features([feature1, feature2])
        self.FeaturesEqual(result, [
            feature1,
            Feature(LineString([(1, 1.000001), (2, 2)]), f1data)
        ])

    def test_three_features_merge_and_dont_merge(self):
        f1data = {'feature': 1, 'test 1': 'data 23'}
        f2data = {'feature': 2, 'test 2': 'data 34'}
        f3data = {'feature': 3, 'test 3': 'data 45'}
        feature1 = Feature(LineString([(0, 0), (1, 1)]), f1data)
        feature2 = Feature(LineString([(1, 1.000001), (2, 2)]), f2data)
        feature3 = Feature(LineString([(2, 2), (3, 3)]), f3data)
        result = geometry_merge.merge_features([feature1, feature2, feature3])
        self.FeaturesEqual(result, [
            feature1,
            Feature(LineString([(1, 1.000001), (2, 2), (3, 3)]), f1data)
        ])

if __name__ == '__main__':
    unittest.main()