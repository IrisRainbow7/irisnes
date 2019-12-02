import unittest
import irisnes

class TestCassette(unittest.TestCase):
    def test_cassette(self):
        self.assertTrue(irisnes.Cassette('sample.nes'))

    def test_sprite(self):
        self.assertEqual(irisnes.Cassette('sample.nes').sprite(72), [250, 453, 423, 445, 437, 445, 373, 127])
