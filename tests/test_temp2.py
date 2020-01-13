import unittest
import irisnes
import os

class TestTemp(unittest.TestCase):
    def test_temp(self):
        nes = irisnes.NES('nestest.nes')
        n = 0
        for i in range(n):
            nes.cpu.run()
        for i in range(10000):
            print(i+n,end=': ')
            a=nes.cpu.run()
            b=input()
        self.assertTrue(os.path.exists('C:\\Users\\Denken\\Desktop\\irisnes\\screen.png'))

