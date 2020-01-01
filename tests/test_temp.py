import unittest
import irisnes
import os

class TestTemp(unittest.TestCase):
    def test_temp(self):
        nes = irisnes.NES('sample1.nes')
        nes.start()
        self.assertTrue(os.path.exists('C:\\Users\\Denken\\Desktop\\irisnes\\screen.png'))

