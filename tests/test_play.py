import unittest
import irisnes
import os

class TestPlay(unittest.TestCase):
    def test_play(self):
        nes = irisnes.NES('nestest.nes')


        nes.start()


        self.assertTrue(os.path.exists('C:\\Users\\Denken\\Desktop\\irisnes\\screen.png'))

