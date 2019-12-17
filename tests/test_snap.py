import unittest
import allfed_spatial.geometry.snap as geometry_snap
from shapely.geometry import LineString
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