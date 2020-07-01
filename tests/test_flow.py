import os
import tempfile
import unittest
import allfed_spatial.features.io as featureIO
import fiona
import math
import networkx as nx
from shapely.geometry import LineString, LinearRing, MultiPolygon, Point, Polygon
from allfed_spatial.features.feature import Feature
from tests.test_geometry_line import LineBaseTest

# TODO: apply driver='ESRI Shapefile' to fiona writing in order to open with nx

class Test_preprocess_graph(LineBaseTest):
	def test_missing_file(self):
		with tempfile.TemporaryDirectory("-allfed-spatial-test") as tempdir:
			filename = os.path.join(tempdir, "testfile.shp")

			with self.assertRaises(RuntimeError):
				G = nx.read_shp(tempdir)

	def test_empty_file(self):
		with tempfile.TemporaryDirectory("-allfed-spatial-test") as tempdir:
			filename = os.path.join(tempdir, "testfile.shp")
			schema = featureIO.get_feature_schema(Feature(Point(0, 0)))

			featureIO.write_shape([], [], schema, filename)

			G = nx.read_shp(tempdir)
			self.assertEqual(G.number_of_nodes(), 0, "Expected zero nodes")
			self.assertEqual(G.number_of_edges(), 0, "Expected zero edges")

	def test_single_node(self):
		with tempfile.TemporaryDirectory("-allfed-spatial-test") as tempdir:
			filename = os.path.join(tempdir, "testfile.shp")
			features = [
				Feature(Point(4, 2)), {"some": "data"})
			]

			featureIO.write_features(features, filename)

			G = nx.read_shp(tempdir)
			self.assertEqual(G.number_of_nodes(), 1, "Expected one node")
			self.assertEqual(G.number_of_edges(), 0, "Expected zero edges")

	def test_single_edge(self):
		self.fail("Test needs to be implimented")

	def test_four_way_intersection(self):
		self.fail("Test needs to be implimented")

	def test_loop(self):
		self.fail("Test needs to be implimented")

	def test_figure_eight(self):
		self.fail("Test needs to be implimented")