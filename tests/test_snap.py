import rtree
import unittest
import allfed_spatial.geometry.snap as geometry_snap
from shapely.geometry import Point, LineString, Polygon
from allfed_spatial.features.feature import Feature
from tests.test_geometry_line import LineBaseTest

class Test_snap_linestrings(LineBaseTest):
	def test_no_lines(self):
		lines = []
		radius = 10
		result = geometry_snap.snap_linestrings(radius, lines)
		self.assertEqual(result, [])

	def test_single_snap_start_to_end(self):
		lines = [
			LineString([(0, 0), (100, 100)]),
			LineString([(0, -100), (0, -5)])
		]
		radius = 10
		result = geometry_snap.snap_linestrings(radius, lines)
		self.LinesEquivalent(result, [
			LineString([(0,-5), (0, 0), (100, 100)]),
			LineString([(0, -100), (0, -5)])
		])

	def test_single_snap_end_to_start(self):
		lines = [
			LineString([(100, 100), (0, 0)]),
			LineString([(0, -5), (0, -100)])
		]
		radius = 10
		result = geometry_snap.snap_linestrings(radius, lines)
		self.LinesEquivalent(result, [
			LineString([(100, 100), (0, 0), (0, -5)]),
			LineString([(0, -5), (0, -100)])
		])

	def test_single_snap_start_to_start(self):
		lines = [
			LineString([(0, 0), (100, 100)]),
			LineString([(0, -5), (0, -100)])
		]
		radius = 10
		result = geometry_snap.snap_linestrings(radius, lines)
		self.LinesEquivalent(result, [
			LineString([(0,-5), (0, 0), (100, 100)]),
			LineString([(0, -5), (0, -100)])
		])

	def test_single_snap_end_to_end(self):
		lines = [
			LineString([(100, 100), (0, 0)]),
			LineString([(0, -100), (0, -5)])
		]
		radius = 10
		result = geometry_snap.snap_linestrings(radius, lines)
		self.LinesEquivalent(result, [
			LineString([(100, 100), (0, 0), (0, -5)]),
			LineString([(0, -100), (0, -5)])
		])

	def test_single_snap_start_to_middle(self):
		lines = [
			LineString([(0, 0), (100, 100)]),
			LineString([(0, -100), (0, -5), (100, -5)])
		]
		radius = 10
		result = geometry_snap.snap_linestrings(radius, lines)
		self.LinesEquivalent(result, [
			LineString([(0, -5), (0, 0), (100, 100)]),
			LineString([(0, -100), (0, -5), (100, -5)])
		])

	def test_single_snap_middle_to_end(self):
		lines = [
			LineString([(100, 100), (0, 0), (0, 100)]),
			LineString([(0, -100), (0, -5)])
		]
		radius = 10
		result = geometry_snap.snap_linestrings(radius, lines)
		self.LinesEquivalent(result, [
			LineString([(100, 100), (0, 0), (0, 100)]),
			LineString([(0, -100), (0, -5), (0, 0)])
		])

	def test_snap_prioritiezes_first_snap(self):
		l1 = LineString([(0, 0), (100, 100)])
		l2 = LineString([(0, -100), (0, -5)])
		lines1 = [
			l1,
			l2
		]
		lines2 = [
			l2,
			l1
		]
		radius = 10
		result1 = geometry_snap.snap_linestrings(radius, lines1)
		result2 = geometry_snap.snap_linestrings(radius, lines2)
		self.LinesEquivalent(result1, [
			LineString([(0,-5), (0, 0), (100, 100)]),
			LineString([(0, -100), (0, -5)])
		])
		self.LinesEquivalent(result2, [
			LineString([(0, -100), (0, -5), (0, 0)]),
			LineString([(0, 0), (100, 100)])
		])

	def test_multi_snap_with_central_point(self):
		lines = [
			LineString([(0, 5), (0, 100)]),
			LineString([(0, -5), (0, -100)]),
			LineString([(5, 0), (100, 0)]),
			LineString([(-5, 0), (-100, 0)]),
			LineString([(0, 0), (0, 0)])
		]
		radius = 10
		result = geometry_snap.snap_linestrings(radius, lines)
		self.LinesEquivalent(result, [
			LineString([(0, 0), (0, 5), (0, 100)]),
			LineString([(0, 0), (0, -5), (0, -100)]),
			LineString([(0, 0), (5, 0), (100, 0)]),
			LineString([(0, 0), (-5, 0), (-100, 0)]),
			LineString([(0, 0), (0, 0)])
		])

	def test_multi_snap_without_central_point(self):
		lines = [
			LineString([(0, 5), (0, 100)]),
			LineString([(0, -5), (0, -100)]),
			LineString([(5, 0), (100, 0)]),
			LineString([(-5, 0), (-100, 0)])
		]
		radius = 10
		result = geometry_snap.snap_linestrings(radius, lines)
		self.LinesEquivalent(result, [
			LineString([(5, 0), (0, 5), (0, 100)]),
			LineString([(-5, 0), (0, -5), (0, -100)]),
			LineString([(5, 0), (100, 0)]),
			LineString([(-5, 0), (-100, 0)])
		])

	def test_snap_both_ends(self):
		lines = [
			LineString([(0, 0), (100, 100)]),
			LineString([(100, 95), (5, 0)])
		]
		radius = 10
		result = geometry_snap.snap_linestrings(radius, lines)
		self.LinesEquivalent(result, [
			LineString([(5, 0), (0, 0), (100, 100), (100, 95)]),
			LineString([(100, 95), (5, 0)])
		])

	def test_no_snap_when_intersecting(self):
		lines = [
			LineString([(0, 0), (100, 100)]),
			LineString([(100, 105), (0, -5)])
		]
		radius = 10
		result = geometry_snap.snap_linestrings(radius, lines)
		self.LinesEquivalent(result, [
			LineString([(0, 0), (100, 100)]),
			LineString([(100, 105), (0, -5)])
		])

	def test_snap_to_non_point(self):
		lines = [
			LineString([(0, 0), (100, 100)]),
			LineString([(-5, 0), (0, -5)])
		]
		radius = 10
		result = geometry_snap.snap_linestrings(radius, lines)
		self.LinesEquivalent(result, [
			LineString([(-2.5, -2.5), (0, 0), (100, 100)]),
			LineString([(-5, 0), (0, -5)])
		])

class Test_intersects_with_index(unittest.TestCase):
	def test_no_geoms_None(self):
		geoms = []
		geomIdx = -1
		index = rtree.index.Index()
		for idx, geom in enumerate(geoms):
			index.insert(idx, geom)
		with self.assertRaises(AttributeError):
			geometry_snap.intersects_with_index(geomIdx, index, None, geoms)

	def test_no_geoms_not_None(self):
		geoms = []
		geomIdx = -1
		index = rtree.index.Index()
		for idx, geom in enumerate(geoms):
			index.insert(idx, geom)
		self.assertEqual(geometry_snap.intersects_with_index(geomIdx, index, Point(0, 0), geoms), False)

	def test_one_geom(self):
		geoms = [
			Point(0, 0)
		]
		geomIdx = 0
		index = rtree.index.Index()
		for idx, geom in enumerate(geoms):
			index.insert(idx, geom.bounds)
		self.assertEqual(geometry_snap.intersects_with_index(geomIdx, index, geoms[geomIdx], geoms), False)

	def test_two_geoms_no_overlap(self):
		geoms = [
			Point(0, 0),
			Point(1, 1)
		]
		index = rtree.index.Index()
		for idx, geom in enumerate(geoms):
			index.insert(idx, geom.bounds)

		geomIdx = 0
		self.assertEqual(geometry_snap.intersects_with_index(geomIdx, index, geoms[geomIdx], geoms), False)
		geomIdx = 1
		self.assertEqual(geometry_snap.intersects_with_index(geomIdx, index, geoms[geomIdx], geoms), False)

	def test_two_geoms_overlap(self):
		geoms = [
			Point(0, 0),
			Point(0, 0)
		]
		index = rtree.index.Index()
		for idx, geom in enumerate(geoms):
			index.insert(idx, geom.bounds)

		geomIdx = 0
		self.assertEqual(geometry_snap.intersects_with_index(geomIdx, index, geoms[geomIdx], geoms), True)
		geomIdx = 1
		self.assertEqual(geometry_snap.intersects_with_index(geomIdx, index, geoms[geomIdx], geoms), True)

	def test_two_geoms_no_overlap_when_nested(self):
		geoms = [
			Point(0, 0),
			LineString([(-1, -1), (1, -1), (1, 1), (-1, 1), (-1, -1)])
		]
		index = rtree.index.Index()
		for idx, geom in enumerate(geoms):
			index.insert(idx, geom.bounds)

		geomIdx = 0
		self.assertEqual(geometry_snap.intersects_with_index(geomIdx, index, geoms[geomIdx], geoms), False)
		geomIdx = 1
		self.assertEqual(geometry_snap.intersects_with_index(geomIdx, index, geoms[geomIdx], geoms), False)

	def test_two_geoms_overlap_when_Polgon(self):
		geoms = [
			Point(0, 0),
			Polygon([(-1, -1), (1, -1), (1, 1), (-1, 1), (-1, -1)])
		]
		index = rtree.index.Index()
		for idx, geom in enumerate(geoms):
			index.insert(idx, geom.bounds)

		geomIdx = 0
		self.assertEqual(geometry_snap.intersects_with_index(geomIdx, index, geoms[geomIdx], geoms), True)
		geomIdx = 1
		self.assertEqual(geometry_snap.intersects_with_index(geomIdx, index, geoms[geomIdx], geoms), True)

	def test_two_geoms_but_bad_index(self):
		geoms = [
			Point(0, 0),
			Point(0, 0)
		]
		index = rtree.index.Index()
		for idx, geom in enumerate(geoms):
			index.insert(0, geom.bounds)

		geomIdx = 0
		self.assertEqual(geometry_snap.intersects_with_index(geomIdx, index, Point(0, 0), geoms), False)