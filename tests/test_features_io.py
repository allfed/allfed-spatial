import os
import tempfile
import unittest
import allfed_spatial.features.io as featureIO
import fiona
from shapely.geometry import LineString, LinearRing, MultiPolygon, Point, Polygon
from allfed_spatial.features.feature import Feature
from tests.test_geometry_line import LineBaseTest

class Test_get_fiona_type(unittest.TestCase):
	def test_all_cases(self):
		self.assertEqual(featureIO.get_fiona_type(0), 'int:16')
		self.assertEqual(featureIO.get_fiona_type(0.0), 'float:16')
		self.assertEqual(featureIO.get_fiona_type('0'), 'str:250')
		with self.assertRaises(ValueError):
			featureIO.get_fiona_type(None)

class Test_get_shapely_class_from_geom_type(unittest.TestCase):
	def test_all_cases(self):
		self.assertEqual(
			featureIO.get_shapely_class_from_geom_type('LineString'),
			LineString)
		self.assertEqual(
			featureIO.get_shapely_class_from_geom_type('Point'),
			Point)
		self.assertEqual(
			featureIO.get_shapely_class_from_geom_type('Polygon'),
			Polygon)
		self.assertEqual(
			featureIO.get_shapely_class_from_geom_type('MultiPolygon'),
			MultiPolygon)
		with self.assertRaises(ValueError):
			featureIO.get_shapely_class_from_geom_type('Something else')


class Test_get_feature_schema(unittest.TestCase):
	def test_line_string_geometry(self):
		feature = Feature(
			LineString([(0, 0), (1, 1)]),
			{ "test": "data" })
		self.assertEqual(
			featureIO.get_feature_schema(feature),
			{"geometry": "LineString", "properties": {"test": "str:250"}})

	def test_point_geometry(self):
		feature = Feature(
			Point(0, 0),
			{ "test": "data" })
		self.assertEqual(
			featureIO.get_feature_schema(feature),
			{"geometry": "Point", "properties": {"test": "str:250"}})

	def test_polygon_geometry(self):
		feature = Feature(
			Polygon([(0, 0), (1, 1), (0, 1)]),
			{ "test": "data" })
		self.assertEqual(
			featureIO.get_feature_schema(feature),
			{"geometry": "Polygon", "properties": {"test": "str:250"}})

	def test_multi_polygon_geometry(self):
		feature = Feature(
			MultiPolygon([Polygon([(0, 0), (1, 1), (0, 1)])]),
			{ "test": "data" })
		self.assertEqual(
			featureIO.get_feature_schema(feature),
			{"geometry": "MultiPolygon", "properties": {"test": "str:250"}})

	def test_other_geometry(self):
		feature = Feature(
			LinearRing([(0, 0), (1, 1), (0, 1)]),
			{ "test": "data" })
		# other types will fail later in the process
		self.assertEqual(
			featureIO.get_feature_schema(feature),
			{"geometry": "LinearRing", "properties": {"test": "str:250"}})

	def test_string_data(self):
		feature = Feature(
			LineString([(0, 0), (1, 1)]),
			{ "test": "data" })
		self.assertEqual(
			featureIO.get_feature_schema(feature),
			{"geometry": "LineString", "properties": {"test": "str:250"}})

	def test_int_data(self):
		feature = Feature(
			LineString([(0, 0), (1, 1)]),
			{ "test": 123 })
		self.assertEqual(
			featureIO.get_feature_schema(feature),
			{"geometry": "LineString", "properties": {"test": "int:16"}})

	def test_float_data(self):
		feature = Feature(
			LineString([(0, 0), (1, 1)]),
			{ "test": 123.4 })
		self.assertEqual(
			featureIO.get_feature_schema(feature),
			{"geometry": "LineString", "properties": {"test": "float:16"}})

	def test_invalid_data_types(self):
		with self.assertRaises(ValueError):
			feature = Feature(
				LineString([(0, 0), (1, 1)]),
				{ "test": None })
			featureIO.get_feature_schema(feature)

		with self.assertRaises(ValueError):
			feature = Feature(
				LineString([(0, 0), (1, 1)]),
				{ "test": [0, 1, 2] })
			featureIO.get_feature_schema(feature)

		with self.assertRaises(ValueError):
			feature = Feature(
				LineString([(0, 0), (1, 1)]),
				{ "test": (0, 1, 2) })
			featureIO.get_feature_schema(feature)

		with self.assertRaises(ValueError):
			feature = Feature(
				LineString([(0, 0), (1, 1)]),
				{ "test": {"more": "test", "data": 123} })
			featureIO.get_feature_schema(feature)

		with self.assertRaises(ValueError):
			feature = Feature(
				LineString([(0, 0), (1, 1)]),
				{ "test": object() })
			featureIO.get_feature_schema(feature)

		with self.assertRaises(ValueError):
			feature = Feature(
				LineString([(0, 0), (1, 1)]),
				{ "test": Point(0, 0) })
			featureIO.get_feature_schema(feature)

complete_test_data_1 = {
	"int": 123,
	"float": 123.4,
	"string": "this is a test string",
	"uniqueKey": 1
}

complete_test_data_2 = {
	"int": 123,
	"float": 123.4,
	"string": "this is a test string",
	"uniqueKey": 2
}

class Test_write_features(LineBaseTest):
	def test_line_string(self):
		with tempfile.TemporaryDirectory("-allfed-spatial-test") as tempdir:
			filename = os.path.join(tempdir, "testfile.file")

			feature1 = Feature(
				LineString([(0, 0), (1, 1)]),
				complete_test_data_1)
			feature2 = Feature(
				LineString([(2, 2), (3, 3)]),
				complete_test_data_2)

			featuresToDisk = [feature1, feature2]
			featureIO.write_features(featuresToDisk, filename)
			featuresFromDisk = featureIO.load_features(filename)
			self.FeaturesEqual(featuresFromDisk, featuresToDisk)

	def test_point(self):
		with tempfile.TemporaryDirectory("-allfed-spatial-test") as tempdir:
			filename = os.path.join(tempdir, "testfile.file")

			feature1 = Feature(
				Point(0, 0),
				complete_test_data_1)
			feature2 = Feature(
				Point(1, 1),
				complete_test_data_2)

			featuresToDisk = [feature1, feature2]
			featureIO.write_features(featuresToDisk, filename)
			featuresFromDisk = featureIO.load_features(filename)
			self.FeaturesEqual(featuresFromDisk, featuresToDisk)

	def test_polygon(self):
		with tempfile.TemporaryDirectory("-allfed-spatial-test") as tempdir:
			filename = os.path.join(tempdir, "testfile.file")

			feature1 = Feature(
				Polygon([(0, 0), (1, 1), (0, 1)]),
				complete_test_data_1)
			feature2 = Feature(
				Polygon([(0, 0), (1, 1), (1, 0)]),
				complete_test_data_2)

			featuresToDisk = [feature1, feature2]
			featureIO.write_features(featuresToDisk, filename)
			featuresFromDisk = featureIO.load_features(filename)
			self.FeaturesEqual(featuresFromDisk, featuresToDisk)

	def test_multi_polygon(self):
		with tempfile.TemporaryDirectory("-allfed-spatial-test") as tempdir:
			filename = os.path.join(tempdir, "testfile.file")

			feature1 = Feature(
				MultiPolygon([
					Polygon([(0, 0), (1, 1), (0, 1)]),
					Polygon([(0, 0), (1, 1), (1, 0)])]),
				complete_test_data_1)
			feature2 = Feature(
				MultiPolygon([
					Polygon([(1, 1), (2, 2), (1, 2)]),
					Polygon([(1, 1), (2, 2), (2, 1)])]),
				complete_test_data_2)

			featuresToDisk = [feature1, feature2]
			featureIO.write_features(featuresToDisk, filename)
			featuresFromDisk = featureIO.load_features(filename)
			self.FeaturesEqual(featuresFromDisk, featuresToDisk)

	def test_other_geom(self):
		"""Other geometry is silently lost, no exceptions stop the process"""
		with tempfile.TemporaryDirectory("-allfed-spatial-test") as tempdir:
			filename = os.path.join(tempdir, "testfile.file")

			feature1 = Feature(
				LinearRing([(0, 0), (1, 1), (0, 1)]),
				complete_test_data_1)

			featuresToDisk = [feature1]
			featureIO.write_features(featuresToDisk, filename)
			featuresFromDisk = featureIO.load_features(filename)
			self.assertEqual(featuresFromDisk, [])

	def test_mixed_geom(self):
		with tempfile.TemporaryDirectory("-allfed-spatial-test") as tempdir:
			filename = os.path.join(tempdir, "testfile.file")

			feature1 = Feature(
				LineString([(0, 0), (1, 1)]),
				complete_test_data_1)
			feature2 = Feature(
				Point(20, 20),
				complete_test_data_2)

			featuresToDisk = [feature1, feature2]
			with self.assertRaises(fiona.errors.GeometryTypeValidationError):
				featureIO.write_features(featuresToDisk, filename)

class Test_write_shape(unittest.TestCase):
	def test_line_string(self):
		self.fail("test to be written")

if __name__ == '__main__':
	unittest.main()