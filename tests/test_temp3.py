import unittest
import irisnes
import os

class TestTemp(unittest.TestCase):
    def test_temp(self):
        nes = irisnes.NES('nestest.nes')
        with open('nestest.log') as f:
            s = f.readlines()

        b=[0xC000, 0, 0, 0, 0x24, 0xfd]
        for i in range(10000):
            #gagag=input()
            print(i,end=': ')
            a=nes.cpu.run()
            print("PC: {} A: {} X: {} Y: {} P: {} SP: {}".format(hex(b[0]),hex(b[1]),hex(b[2]),hex(b[3]),hex(b[4]),hex(b[5])))
            self.assertEqual(s[i][:4],str(hex(b[0]))[2:].upper().zfill(4))
            self.assertEqual(s[i][50:52],str(hex(b[1]))[2:].upper().zfill(2))
            self.assertEqual(s[i][55:57],str(hex(b[2]))[2:].upper().zfill(2))
            self.assertEqual(s[i][60:62],str(hex(b[3]))[2:].upper().zfill(2))
            self.assertEqual(s[i][65:67],str(hex(b[4]))[2:].upper().zfill(2))
            self.assertEqual(s[i][71:73],str(hex(b[5]))[2:].upper().zfill(2))
            b=a
        self.assertTrue(os.path.exists('C:\\Users\\Denken\\Desktop\\irisnes\\screen.png'))

