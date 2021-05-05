import unittest
import irisnes
import os

class TestPlay(unittest.TestCase):
    def test_play(self):
        file_name = 'oam3.nes'
        nes = irisnes.NES(file_name)


        nes.start()


        self.assertTrue(os.path.exists('C:\\Users\\Denken\\Desktop\\irisnes\\screen.png'))

