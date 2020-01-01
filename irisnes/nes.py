import irisnes
from PIL import Image
import numpy as np
import sys

class nes:

    def __init__(self, nes_file_path):
        self.nes_file_path = nes_file_path
        self.cassette = irisnes.Cassette(nes_file_path)
        self.cpu_bus = irisnes.CPUBus(self)
        self.ppu_bus = irisnes.PPUBus(self)
        self.cpu = irisnes.CPU(self)
        self.ppu = irisnes.PPU(self)

    def start(self)
        cycle = 0
        cycle += self.cpu.run()
        image = self.ppu.run(cycle * 3)
        if len(image) > 0:
            Image.fromarray(np.uint8(image)).save('screen.png')
            sys.exit()
