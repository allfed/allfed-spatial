import os
import tempfile
import unittest
import allfed_spatial.features.io as featureIO
import fiona
import math
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

diff_schema_test_data = {
	"int": 123,
	"float": 123.4,
	"string": "this is a test string",
	"uniqueKey": 3,
	"new Key": "breaks the schema"
}

diff_schema_convertable_string_test_data = {
	"int": 123,
	"float": 123.4,
	"string": "the unique key is a string, technically the schema is different",
	"uniqueKey": "3"
}

diff_schema_convertable_float_test_data = {
	"int": 123,
	"float": 123.4,
	"string": "the unique key is a float, technically the schema is different",
	"uniqueKey": 3.5
}

diff_schema_unconvertable_string_test_data = {
	"int": 123,
	"float": 123.4,
	"string": "the unique key is not convertable to an int",
	"uniqueKey": "NaN"
}

diff_schema_unconvertable_float_test_data = {
	"int": 123,
	"float": 123.4,
	"string": "the unique key is not convertable to an int",
	"uniqueKey": math.nan
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

	def test_different_schema(self):
		with tempfile.TemporaryDirectory("-allfed-spatial-test") as tempdir:
			filename = os.path.join(tempdir, "testfile.file")

			feature1 = Feature(
				LineString([(0, 0), (1, 1)]),
				complete_test_data_1)
			feature2 = Feature(
				LineString([(2, 2), (3, 3)]),
				diff_schema_test_data)

			featuresToDisk = [feature1, feature2]
			with self.assertRaises(ValueError):
				featureIO.write_features(featuresToDisk, filename)

	def test_different_schema_convertable_string(self):
		"""Note that the string is converted to an int"""
		with tempfile.TemporaryDirectory("-allfed-spatial-test") as tempdir:
			filename = os.path.join(tempdir, "testfile.file")

			feature1 = Feature(
				LineString([(0, 0), (1, 1)]),
				complete_test_data_1)
			feature2 = Feature(
				LineString([(2, 2), (3, 3)]),
				diff_schema_convertable_string_test_data)

			featuresToDisk = [feature1, feature2]
			featureIO.write_features(featuresToDisk, filename)

			featuresFromDisk = featureIO.load_features(filename)

			modifiedFeaturesFromDisk = featureIO.load_features(filename)
			modifiedFeaturesFromDisk[1].data["uniqueKey"] = "3"

			self.assertNotEqual(featuresFromDisk[1].data["uniqueKey"], "3")
			self.assertEqual(featuresFromDisk[1].data["uniqueKey"], 3)
			self.FeaturesEqual(modifiedFeaturesFromDisk, featuresToDisk)

	def test_different_schema_convertable_float(self):
		"""Note that the float is converted to an int"""
		with tempfile.TemporaryDirectory("-allfed-spatial-test") as tempdir:
			filename = os.path.join(tempdir, "testfile.file")

			feature1 = Feature(
				LineString([(0, 0), (1, 1)]),
				complete_test_data_1)
			feature2 = Feature(
				LineString([(2, 2), (3, 3)]),
				diff_schema_convertable_float_test_data)

			featuresToDisk = [feature1, feature2]
			featureIO.write_features(featuresToDisk, filename)

			featuresFromDisk = featureIO.load_features(filename)

			modifiedFeaturesFromDisk = featureIO.load_features(filename)
			modifiedFeaturesFromDisk[1].data["uniqueKey"] = 3.5

			self.assertNotEqual(featuresFromDisk[1].data["uniqueKey"], 3.5)
			self.assertEqual(featuresFromDisk[1].data["uniqueKey"], 3)
			self.FeaturesEqual(modifiedFeaturesFromDisk, featuresToDisk)

	def test_different_schema_unconvertable_string(self):
		"""Note that the string value is dropped and a default of 0 is used"""
		with tempfile.TemporaryDirectory("-allfed-spatial-test") as tempdir:
			filename = os.path.join(tempdir, "testfile.file")

			feature1 = Feature(
				LineString([(0, 0), (1, 1)]),
				complete_test_data_1)
			feature2 = Feature(
				LineString([(2, 2), (3, 3)]),
				diff_schema_unconvertable_string_test_data)

			featuresToDisk = [feature1, feature2]
			featureIO.write_features(featuresToDisk, filename)

			featuresFromDisk = featureIO.load_features(filename)

			modifiedFeaturesFromDisk = featureIO.load_features(filename)
			modifiedFeaturesFromDisk[1].data["uniqueKey"] = "NaN"

			self.assertNotEqual(featuresFromDisk[1].data["uniqueKey"], "NaN")
			self.assertEqual(featuresFromDisk[1].data["uniqueKey"], 0)
			self.FeaturesEqual(modifiedFeaturesFromDisk, featuresToDisk)

	def test_different_schema_unconvertable_float(self):
		"""Note that the NaN value is dropped,
		it seems like int_64(1<<64) is used
		i.e. -(2**63), the minimum 64 bit int value
		
		odd given that we map to int:16,
		TODO: maybe we should be mapping to int:64 instead,
		we'll find out in the write_shape tests."""
		with tempfile.TemporaryDirectory("-allfed-spatial-test") as tempdir:
			filename = os.path.join(tempdir, "testfile.file")

			feature1 = Feature(
				LineString([(0, 0), (1, 1)]),
				complete_test_data_1)
			feature2 = Feature(
				LineString([(2, 2), (3, 3)]),
				diff_schema_unconvertable_float_test_data)

			featuresToDisk = [feature1, feature2]
			featureIO.write_features(featuresToDisk, filename)

			featuresFromDisk = featureIO.load_features(filename)

			self.assertEqual(featuresFromDisk[1].data["uniqueKey"], -(2**63))
			self.assertTrue(math.isnan(featuresToDisk[1].data["uniqueKey"]))

class Test_write_shape(LineBaseTest):

	# test geometry
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

			geoms = [f.geom for f in featuresToDisk]
			data = [f.data for f in featuresToDisk]

			schema = featureIO.get_feature_schema(featuresToDisk[0])

			featureIO.write_shape(geoms, data, schema, filename)
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

			geoms = [f.geom for f in featuresToDisk]
			data = [f.data for f in featuresToDisk]

			schema = featureIO.get_feature_schema(featuresToDisk[0])

			featureIO.write_shape(geoms, data, schema, filename)
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

			geoms = [f.geom for f in featuresToDisk]
			data = [f.data for f in featuresToDisk]

			schema = featureIO.get_feature_schema(featuresToDisk[0])

			featureIO.write_shape(geoms, data, schema, filename)
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

			geoms = [f.geom for f in featuresToDisk]
			data = [f.data for f in featuresToDisk]

			schema = featureIO.get_feature_schema(featuresToDisk[0])

			featureIO.write_shape(geoms, data, schema, filename)
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

			geoms = [f.geom for f in featuresToDisk]
			data = [f.data for f in featuresToDisk]

			schema = featureIO.get_feature_schema(featuresToDisk[0])

			featureIO.write_shape(geoms, data, schema, filename)
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

			geoms = [f.geom for f in featuresToDisk]
			data = [f.data for f in featuresToDisk]

			schema = featureIO.get_feature_schema(featuresToDisk[0])

			with self.assertRaises(fiona.errors.GeometryTypeValidationError):
				featureIO.write_shape(geoms, data, schema, filename)

	# test data
	def test_data_mismatch(self):
		with tempfile.TemporaryDirectory("-allfed-spatial-test") as tempdir:
			filename = os.path.join(tempdir, "testfile.file")

			feature1 = Feature(
				Point(0, 0),
				complete_test_data_1)
			feature2 = Feature(
				Point(1, 1),
				diff_schema_test_data)

			featuresToDisk = [feature1, feature2]

			geoms = [f.geom for f in featuresToDisk]
			data = [f.data for f in featuresToDisk]

			schema = featureIO.get_feature_schema(featuresToDisk[0])

			with self.assertRaises(ValueError):
				featureIO.write_shape(geoms, data, schema, filename)

	def test_data_converts(self):
		with tempfile.TemporaryDirectory("-allfed-spatial-test") as tempdir:
			filename = os.path.join(tempdir, "testfile.file")

			feature1 = Feature(
				Point(0, 0),
				complete_test_data_1)
			feature2 = Feature(
				Point(1, 1),
				diff_schema_convertable_string_test_data)

			featuresToDisk = [feature1, feature2]

			geoms = [f.geom for f in featuresToDisk]
			data = [f.data for f in featuresToDisk]

			schema = featureIO.get_feature_schema(featuresToDisk[0])

			featureIO.write_shape(geoms, data, schema, filename)
			featuresFromDisk = featureIO.load_features(filename)

			modifiedFeaturesFromDisk = featureIO.load_features(filename)
			modifiedFeaturesFromDisk[1].data["uniqueKey"] = "3"

			self.assertNotEqual(featuresFromDisk[1].data["uniqueKey"], "3")
			self.assertEqual(featuresFromDisk[1].data["uniqueKey"], 3)
			self.FeaturesEqual(modifiedFeaturesFromDisk, featuresToDisk)

	def test_data_unconvertable(self):
		with tempfile.TemporaryDirectory("-allfed-spatial-test") as tempdir:
			filename = os.path.join(tempdir, "testfile.file")

			feature1 = Feature(
				Point(0, 0),
				complete_test_data_1)
			feature2 = Feature(
				Point(1, 1),
				diff_schema_unconvertable_string_test_data)

			featuresToDisk = [feature1, feature2]

			geoms = [f.geom for f in featuresToDisk]
			data = [f.data for f in featuresToDisk]

			schema = featureIO.get_feature_schema(featuresToDisk[0])

			featureIO.write_shape(geoms, data, schema, filename)
			featuresFromDisk = featureIO.load_features(filename)

			modifiedFeaturesFromDisk = featureIO.load_features(filename)
			modifiedFeaturesFromDisk[1].data["uniqueKey"] = "NaN"

			self.assertNotEqual(featuresFromDisk[1].data["uniqueKey"], "NaN")
			self.assertEqual(featuresFromDisk[1].data["uniqueKey"], 0)
			self.FeaturesEqual(modifiedFeaturesFromDisk, featuresToDisk)

	# test bad schema
	def test_bad_schema(self):
		with tempfile.TemporaryDirectory("-allfed-spatial-test") as tempdir:
			filename = os.path.join(tempdir, "testfile.file")

			feature = Feature(
				Point(0, 0),
				complete_test_data_1)

			featuresToDisk = [feature]

			geoms = [f.geom for f in featuresToDisk]
			data = [f.data for f in featuresToDisk]

			schema = {"This is": "not a schema"}

			with self.assertRaises(Exception):
				featureIO.write_shape(geoms, data, schema, filename)

if __name__ == '__main__':
	unittest.main()