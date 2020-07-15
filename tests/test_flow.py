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

class Test_graph_handling(LineBaseTest):
	def test_missing_file(self):
		with tempfile.TemporaryDirectory("-allfed-spatial-test") as tempdir:
			filename = os.path.join(tempdir, "testfile.shp")

			with self.assertRaises(RuntimeError):
				G = nx.read_shp(tempdir)

	def test_empty_file(self):
		with tempfile.TemporaryDirectory("-allfed-spatial-test") as tempdir:
			filename = os.path.join(tempdir, "testfile.shp")
			schema = featureIO.get_feature_schema(Feature(Point(0, 0)))

			featureIO.write_shape([], [], schema, filename, "ESRI Shapefile")

			G = nx.read_shp(tempdir)
			
			self.assertEqual(G.number_of_nodes(), 0, "Expected zero nodes")
			self.assertEqual(G.number_of_edges(), 0, "Expected zero edges")

	def test_single_node(self):
		with tempfile.TemporaryDirectory("-allfed-spatial-test") as tempdir:
			filename = os.path.join(tempdir, "testfile.shp")
			features = [
				Feature(Point(4, 2), {"some": "data"})
			]

			featureIO.write_features(features, filename, "ESRI Shapefile")

			G = nx.read_shp(tempdir)

			self.assertEqual(G.number_of_nodes(), 1, "Expected one node")
			self.assertNotEqual(G.nodes().get((4, 2)), None)
			self.assertEqual(list(G[(4, 2)]), [])
			self.assertEqual(G.nodes().get((4, 2))["some"], "data")
			for x, y in G.nodes():
				self.assertEqual(x, 4)
				self.assertEqual(y, 2)
				self.assertEqual(G.nodes().get((x, y))["some"], "data")
			self.assertEqual(G.number_of_edges(), 0, "Expected zero edges")

	def test_single_edge(self):
		with tempfile.TemporaryDirectory("-allfed-spatial-test") as tempdir:
			filename = os.path.join(tempdir, "testfile.shp")
			features = [
				Feature(LineString([(4, 2), (1, 2)]), {"some": "data"})
			]

			featureIO.write_features(features, filename, "ESRI Shapefile")

			G = nx.read_shp(tempdir)

			self.assertEqual(G.number_of_nodes(), 2, "Expected two nodes")
			self.assertNotEqual(G.nodes().get((4, 2)), None)
			self.assertNotEqual(G.nodes().get((1, 2)), None)
			self.assertEqual(G.number_of_edges(), 1, "Expected one edge")
			self.assertEqual(list(G[(4, 2)]), [(1, 2)])
			self.assertEqual(list(G[(1, 2)]), [])
			self.assertEqual(G[(4, 2)][(1, 2)]["some"], "data")
			for source, target in G.edges:
				self.assertEqual(source, (4, 2))
				self.assertEqual(target, (1, 2))
				self.assertEqual(G[source][target]["some"], "data")

	def test_four_way_intersection(self):
		with tempfile.TemporaryDirectory("-allfed-spatial-test") as tempdir:
			filename = os.path.join(tempdir, "testfile.shp")
			features = [
				Feature(LineString([(0, 0), (1, 0)]), {"some": "data"}),
				Feature(LineString([(0, 0), (0, 1)]), {"some": "data"}),
				Feature(LineString([(0, 0), (-1, 0)]), {"some": "data"}),
				Feature(LineString([(0, 0), (0, -1)]), {"some": "data"}),
				Feature(LineString([(1, 0), (0, 0)]), {"some": "data"}),
				Feature(LineString([(0, 1), (0, 0)]), {"some": "data"}),
				Feature(LineString([(-1, 0), (0, 0)]), {"some": "other data"}),
				Feature(LineString([(0, -1), (0, 0)]), {"some": "other data"}),
			]

			featureIO.write_features(features, filename, "ESRI Shapefile")

			G = nx.read_shp(tempdir)

			self.assertEqual(G.number_of_nodes(), 5, "Expected five nodes")
			self.assertFalse("some" in G.nodes().get((0, 0)).keys())
			self.assertFalse("some" in G.nodes().get((1, 0)).keys())
			self.assertFalse("some" in G.nodes().get((0, 1)).keys())
			self.assertFalse("some" in G.nodes().get((-1, 0)).keys())
			self.assertFalse("some" in G.nodes().get((0, -1)).keys())
			self.assertEqual(G.number_of_edges(), 8, "Expected four edges")
			self.assertEqual(G[(0, 0)][(1, 0)]["some"], "data")
			self.assertEqual(G[(0, 0)][(0, 1)]["some"], "data")
			self.assertEqual(G[(0, 0)][(-1, 0)]["some"], "data")
			self.assertEqual(G[(0, 0)][(0, -1)]["some"], "data")
			self.assertEqual(G[(1, 0)][(0, 0)]["some"], "data")
			self.assertEqual(G[(0, 1)][(0, 0)]["some"], "data")
			self.assertEqual(G[(-1, 0)][(0, 0)]["some"], "other data")
			self.assertEqual(G[(0, -1)][(0, 0)]["some"], "other data")
			self.assertEqual(list(G[(0, 0)]), [(1, 0), (0, 1), (-1, 0), (0, -1)])
			self.assertEqual(list(G[(1, 0)]), [(0, 0)])
			self.assertEqual(list(G[(0, 1)]), [(0, 0)])
			self.assertEqual(list(G[(-1, 0)]), [(0, 0)])
			self.assertEqual(list(G[(0, -1)]), [(0, 0)])

	def test_loop(self):
		with tempfile.TemporaryDirectory("-allfed-spatial-test") as tempdir:
			filename = os.path.join(tempdir, "testfile.shp")
			features = [
				Feature(LineString([(1, 0), (0, 1)]), {"some": "data"}),
				Feature(LineString([(0, 1), (-1, 0)]), {"some": "data"}),
				Feature(LineString([(-1, 0), (0, -1)]), {"some": "data"}),
				Feature(LineString([(0, -1), (1, 0)]), {"some": "data"}),
			]

			featureIO.write_features(features, filename, "ESRI Shapefile")

			G = nx.read_shp(tempdir)

			self.assertEqual(G.number_of_nodes(), 4, "Expected four nodes")
			self.assertNotEqual(G.nodes().get((1, 0)), None)
			self.assertNotEqual(G.nodes().get((0, 1)), None)
			self.assertNotEqual(G.nodes().get((-1, 0)), None)
			self.assertNotEqual(G.nodes().get((0, -1)), None)
			self.assertEqual(G.number_of_edges(), 4, "Expected four edges")
			self.assertEqual(list(G[(1, 0)]), [(0, 1)])
			self.assertEqual(list(G[(0, 1)]), [(-1, 0)])
			self.assertEqual(list(G[(-1, 0)]), [(0, -1)])
			self.assertEqual(list(G[(0, -1)]), [(1, 0)])
			for source, target in G.edges:
				self.assertTrue("some" in G[source][target].keys())

	def test_figure_eight(self):
		with tempfile.TemporaryDirectory("-allfed-spatial-test") as tempdir:
			filename = os.path.join(tempdir, "testfile.shp")
			features = [
				Feature(LineString([(0, 0), (1, -1)]), {"some": "data"}),
				Feature(LineString([(1, -1), (2, 0)]), {"some": "data"}),
				Feature(LineString([(2, 0), (1, 1)]), {"some": "data"}),
				Feature(LineString([(1, 1), (0, 0)]), {"some": "data"}),
				Feature(LineString([(0, 0), (-1, -1)]), {"some": "data"}),
				Feature(LineString([(-1, -1), (-2, 0)]), {"some": "data"}),
				Feature(LineString([(-2, 0), (-1, 1)]), {"some": "data"}),
				Feature(LineString([(-1, 1), (0, 0)]), {"some": "data"}),
			]

			featureIO.write_features(features, filename, "ESRI Shapefile")

			G = nx.read_shp(tempdir)

			self.assertEqual(G.number_of_nodes(), 7, "Expected seven nodes")
			self.assertNotEqual(G.nodes().get((0, 0)), None)
			self.assertNotEqual(G.nodes().get((1, -1)), None)
			self.assertNotEqual(G.nodes().get((2, 0)), None)
			self.assertNotEqual(G.nodes().get((1, 1)), None)
			self.assertNotEqual(G.nodes().get((-1, -1)), None)
			self.assertNotEqual(G.nodes().get((-2, 0)), None)
			self.assertNotEqual(G.nodes().get((-1, 1)), None)
			self.assertEqual(G.number_of_edges(), 8, "Expected four edges")
			self.assertEqual(list(G[(0, 0)]), [(1, -1), (-1, -1)])
			self.assertEqual(list(G[(1, -1)]), [(2, 0)])
			self.assertEqual(list(G[(2, 0)]), [(1, 1)])
			self.assertEqual(list(G[(1, 1)]), [(0, 0)])
			self.assertEqual(list(G[(-1, -1)]), [(-2, 0)])
			self.assertEqual(list(G[(-2, 0)]), [(-1, 1)])
			self.assertEqual(list(G[(-1, 1)]), [(0, 0)])
			for source, target in G.edges:
				self.assertTrue("some" in G[source][target].keys())

class Test_preprocess_graph(LineBaseTest):
	pass