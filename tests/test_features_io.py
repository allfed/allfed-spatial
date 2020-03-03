import unittest
import allfed_spatial.features.io as featureIO
from shapely.geometry import Point, LineString, Polygon
from allfed_spatial.features.feature import Feature
from tests.test_geometry_line import LineBaseTest

class Test_get_fiona_type(unittest.TestCase):
	def test_trivial_types(self):
		self.assertEqual(featureIO.get_fiona_type(0), 'int:16')
		self.assertEqual(featureIO.get_fiona_type(0.0), 'float:16')
		self.assertEqual(featureIO.get_fiona_type('0'), 'str:250')
		with self.assertRaises(ValueError):
			featureIO.get_fiona_type(None)

if __name__ == '__main__':
	unittest.main()