import irisnes
from PIL import Image
import numpy as np
import sys
import time

class NES:

    def __init__(self, nes_file_path):
        self.nes_file_path = nes_file_path
        self.cassette = irisnes.Cassette(nes_file_path)
        self.cpu_bus = irisnes.CPUBus(self)
        self.ppu_bus = irisnes.PPUBus(self)
        self.cpu = irisnes.CPU(self)
        self.ppu = irisnes.PPU(self)

    def start(self):
        t1=[]
        t2=[]
        while(True):
            cycle = 0
            t=time.time()
            cycle += self.cpu.run()
            t1.append(time.time()-t)
            t=time.time()
            image = self.ppu.run(cycle * 3)
            t2.append(time.time()-t)
            if len(image) > 0:
                Image.fromarray(np.uint8(image)).save('screen.png')
                print(sum(t1)/len(t1))
                print(sum(t2)/len(t2))
                print(sum(self.cpu.t1)/len(self.cpu.t1))
                print(sum(self.cpu.t2)/len(self.cpu.t2))
                print(sum(self.cpu.t3)/len(self.cpu.t3))
                print(sum(self.cpu.t4)/len(self.cpu.t4))
                sys.exit()
