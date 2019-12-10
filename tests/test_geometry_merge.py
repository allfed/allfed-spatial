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

if __name__ == '__main__':
    unittest.main()