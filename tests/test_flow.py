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
from allfed_spatial.operations.flow import *

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
			self.assertEqual(G.number_of_edges(), 8, "Expected eight edges")
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
			self.assertEqual(G.number_of_edges(), 8, "Expected eight edges")
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
	def test_none(self):
		with self.assertRaises(AttributeError):
			preprocess_graph(None)

	def test_empty_file(self):
		with tempfile.TemporaryDirectory("-allfed-spatial-test") as tempdir:
			filename = os.path.join(tempdir, "testfile.shp")
			schema = featureIO.get_feature_schema(Feature(Point(0, 0)))

			featureIO.write_shape([], [], schema, filename, "ESRI Shapefile")

			G = nx.read_shp(tempdir)
			preprocess_graph(G)
			
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
			preprocess_graph(G)

			self.assertEqual(G.number_of_nodes(), 1, "Expected one node")
			self.assertEqual(G.number_of_edges(), 0, "Expected zero edges")
			self.assertEqual(G.nodes().get((4, 2))["index"], 0)
			self.assertEqual(G.nodes().get((4, 2))["diff"], 0)

	def test_single_edge(self):
		with tempfile.TemporaryDirectory("-allfed-spatial-test") as tempdir:
			filename = os.path.join(tempdir, "testfile.shp")
			features = [
				Feature(LineString([(4, 2), (1, 2)]), {"some": "data"})
			]

			featureIO.write_features(features, filename, "ESRI Shapefile")

			G = nx.read_shp(tempdir)
			preprocess_graph(G)

			self.assertEqual(G.number_of_nodes(), 2, "Expected two nodes")
			self.assertEqual(G.number_of_edges(), 1, "Expected one edge")
			indexs = []
			for key in G.nodes():
				node = G.nodes()[key]
				self.assertEqual(node['diff'], 0)
				indexs.append(node['index'])
			self.assertEqual(len(indexs), 2)
			indexs.sort()
			self.assertEqual(indexs, list(range(2)))

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
			preprocess_graph(G)

			self.assertEqual(G.number_of_nodes(), 5, "Expected five nodes")
			self.assertEqual(G.number_of_edges(), 8, "Expected eight edges")
			indexs = []
			for key in G.nodes():
				node = G.nodes()[key]
				self.assertEqual(node['diff'], 0)
				indexs.append(node['index'])
			self.assertEqual(len(indexs), 5)
			indexs.sort()
			self.assertEqual(indexs, list(range(5)))

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
			preprocess_graph(G)

			self.assertEqual(G.number_of_nodes(), 4, "Expected four nodes")
			self.assertEqual(G.number_of_edges(), 4, "Expected four edges")
			indexs = []
			for key in G.nodes():
				node = G.nodes()[key]
				self.assertEqual(node['diff'], 0)
				indexs.append(node['index'])
			self.assertEqual(len(indexs), 4)
			indexs.sort()
			self.assertEqual(indexs, list(range(4)))

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
			preprocess_graph(G)

			self.assertEqual(G.number_of_nodes(), 7, "Expected seven nodes")
			self.assertEqual(G.number_of_edges(), 8, "Expected eight edges")
			indexs = []
			for key in G.nodes():
				node = G.nodes()[key]
				self.assertEqual(node['diff'], 0)
				indexs.append(node['index'])
			self.assertEqual(len(indexs), 7)
			indexs.sort()
			self.assertEqual(indexs, list(range(7)))

class Test_setup_min_cost_flow(LineBaseTest):
	#      B--E   
	#     / \/ \  
	#    /  /\  \ 
	#   A--C--F--H
	#    \  \/  / 
	#     \ /\ /  
	#      D--G   
	# 
	# Approx visualization of the graph in use here
	# 
	# A -> B,C,D
	# B -> E,F
	# C -> E,F,G
	# D -> F,G
	# E -> H
	# F -> H
	# G -> H
	def test_conversion(self):
		with tempfile.TemporaryDirectory("-allfed-spatial-test") as tempdir:
			filename = os.path.join(tempdir, "testfile.shp")
			features = [
				Feature(LineString([(0, 0), (1, 1)]), {"cost": 1}),
				Feature(LineString([(0, 0), (1, 0)]), {"cost": 2}),
				Feature(LineString([(0, 0), (1, -1)]), {"cost": 3}),
				Feature(LineString([(1, 1), (2, 1)]), {"cost": 4}),
				Feature(LineString([(1, 1), (2, 0)]), {"cost": 5}),
				Feature(LineString([(1, 0), (2, 1)]), {"cost": 5}),
				Feature(LineString([(1, 0), (2, 0)]), {"cost": 4}),
				Feature(LineString([(1, 0), (2, -1)]), {"cost": 5}),
				Feature(LineString([(1, -1), (2, 0)]), {"cost": 5}),
				Feature(LineString([(1, -1), (2, -1)]), {"cost": 4}),
				Feature(LineString([(2, 1), (3, 0)]), {"cost": 8}),
				Feature(LineString([(2, 0), (3, 0)]), {"cost": 7}),
				Feature(LineString([(2, -1), (3, 0)]), {"cost": 6}),
			]

			featureIO.write_features(features, filename, "ESRI Shapefile")

			G = nx.read_shp(tempdir)

			# no good way to push this into the shapefile given we use a schema
			G.nodes()[(0, 0)]["diff"] = 101
			G.nodes()[(3, 0)]["diff"] = -102

			preprocess_graph(G)

			min_cost_flow = setup_min_cost_flow(G, "cost")

			self.assertEqual(min_cost_flow.NumNodes(), 8, "Expected eight nodes")
			self.assertEqual(min_cost_flow.NumArcs(), 26, "Expected 13 bi-directional arcs")
			
			costs = []
			for idx in range(min_cost_flow.NumArcs()):
				costs.append(min_cost_flow.UnitCost(idx))
			costs.sort()
			# doubled cause bi directional
			self.assertEqual(costs, [1,1,2,2,3,3,4,4,4,4,4,4,5,5,5,5,5,5,5,5,6,6,7,7,8,8])

			diffs = {}
			for idx in range(min_cost_flow.NumNodes()):
				diff = min_cost_flow.Supply(idx)
				if diff not in diffs:
					diffs[diff] = 0
				diffs[diff] += 1
			self.assertEqual(diffs, {101: 1, 0: 6, -102: 1})

class Test_solve_min_cost_flow(unittest.TestCase):
	pass
	# test usage
	# test bi-directional issue?