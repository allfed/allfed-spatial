import unittest
from allfed_spatial.operations import consume


class TestConsume(unittest.TestCase):

    def test_zero_source_consumption(self):
        source = {'remaining': 0}
        sink = {'remaining': 100}
        self.assertEqual(
            consume(source, sink),
            (
                {'remaining': 0},
                {'remaining': 100},
                0
            )
        )

    def test_zero_source_consumption_with_efficiency(self):
        source = {'remaining': 0}
        sink = {'remaining': 100}
        self.assertEqual(
            consume(source, sink, efficiency=0.6),
            (
                {'remaining': 0},
                {'remaining': 100},
                0
            )
        )

    def test_zero_sink_consumption(self):
        source = {'remaining': 100}
        sink = {'remaining': 0}
        self.assertEqual(
            consume(source, sink),
            (
                {'remaining': 100},
                {'remaining': 0},
                0
            )
        )

    def test_zero_sink_consumption_with_efficiency(self):
        source = {'remaining': 100}
        sink = {'remaining': 0}
        self.assertEqual(
            consume(source, sink, efficiency=0.6),
            (
                {'remaining': 100},
                {'remaining': 0},
                0
            )
        )

    def test_full_consumption(self):
        source = {'remaining': 100}
        sink = {'remaining': 100}
        self.assertEqual(
            consume(source, sink),
            (
                {'remaining': 0},
                {'remaining': 0},
                100
            )
        )

    def test_full_consumption_with_efficiency(self):
        source = {'remaining': 100}
        sink = {'remaining': 100}
        self.assertEqual(
            consume(source, sink, efficiency=0.6),
            (
                {'remaining': 0},
                {'remaining': 40},
                60
            )
        )

    def test_partial_source_consumption(self):
        source = {'remaining': 100}
        sink = {'remaining': 50}
        self.assertEqual(
            consume(source, sink),
            (
                {'remaining': 50},
                {'remaining': 0},
                50
            )
        )

    def test_partial_source_consumption_with_efficiency(self):
        source = {'remaining': 100}
        sink = {'remaining': 50}
        self.assertEqual(
            consume(source, sink, efficiency=0.6),
            (
                {'remaining': 16.666666666666657},
                {'remaining': 0},
                50
            )
        )

    def test_partial_sink_consumption(self):
        source = {'remaining': 50}
        sink = {'remaining': 100}
        self.assertEqual(
            consume(source, sink),
            (
                {'remaining': 0},
                {'remaining': 50},
                50
            )
        )

    def test_partial_sink_consumption_with_efficiency(self):
        source = {'remaining': 50}
        sink = {'remaining': 100}
        self.assertEqual(
            consume(source, sink, efficiency=0.6),
            (
                {'remaining': 0},
                {'remaining': 70},
                30
            )
        )


if __name__ == '__main__':
    unittest.main()
