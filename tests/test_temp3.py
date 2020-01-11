import unittest
import irisnes
import os

class TestTemp(unittest.TestCase):
    def test_temp(self):
        nes = irisnes.NES('nestest.nes')
        with open('nestest.log') as f:
            s = f.readlines()

        for i in range(10000):
            print(i,end=': ')
            a=nes.cpu.run()
            self.assertEqual(s[i][16:19],a)
        self.assertTrue(os.path.exists('C:\\Users\\Denken\\Desktop\\irisnes\\screen.png'))

