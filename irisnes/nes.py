import irisnes
from PIL import Image
import numpy as np
import sys
import time
import pygame
from pygame.locals import *

class NES:

    def __init__(self, nes_file_path):
        self.cycle = 0
        self.nes_file_path = nes_file_path
        self.cassette = irisnes.Cassette(nes_file_path)
        self.cpu_bus = irisnes.CPUBus(self)
        self.ppu_bus = irisnes.PPUBus(self)
        self.cpu = irisnes.CPU(self)
        self.ppu = irisnes.PPU(self)
        self.key_status = {'A':False, 'B':False, 'SELECT':False, 'START':False, 'Up':False, 'Down':False, 'Left':False, 'Right':False}

    def start(self):
        pygame.init()
        screen = pygame.display.set_mode((256, 256))
        running = True
        i = 0
        while(running):
            i += 1
            print(i)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == KEYDOWN:
                    if event.key == K_SPACE:
                        self.key_status['START'] = True
                        print('space down')
                    elif event.key == K_UP:
                        self.key_status['Up'] = True
                        print('up')
                    elif event.key == K_DOWN:
                        self.key_status['Down'] = True
                        print('down')
                    elif event.key == K_RIGHT:
                        self.key_status['Right'] = True
                    elif event.key == K_LEFT:
                        self.key_status['Left'] = True
                    elif event.key == K_z:
                        self.key_status['B'] = True
                    elif event.key == K_x:
                        self.key_status['A'] = True

                if event.type == KEYUP:
                    if event.key == K_SPACE:
                        self.key_status['START'] = False
                        print('space up')
                    elif event.key == K_UP:
                        self.key_status['Up'] = False
                    elif event.key == K_DOWN:
                        self.key_status['Down'] = False
                    elif event.key == K_RIGHT:
                        self.key_status['Right'] = False
                    elif event.key == K_LEFT:
                        self.key_status['Left'] = False
                    elif event.key == K_z:
                        self.key_status['B'] = False
                    elif event.key == K_x:
                        self.key_status['A'] = False

            pygame.display.update()
            bg = pygame.surfarray.make_surface(self.make_screen())
            screen.blit(bg, (0,0))

    def dma_start(self, address):
        #print(hex(address))
        data = []
        for i in range(address*0x100, (address+1)*0x100):
            data.append(self.cpu_bus.read(i))
        self.ppu.sprite_ram = data
        self.cycle += 514


    def make_screen(self):
        t1=[]
        t2=[]
        while(True):
            self.cycle = 0
            t=time.time()
            self.cycle += self.cpu.run()
            t1.append(time.time()-t)
            t=time.time()
            image = self.ppu.run(self.cycle * 3)
            t2.append(time.time()-t)
            if len(image) > 0:
                #Image.fromarray(np.uint8(image)).save('screen.png')
                #print('s')
                return(np.rot90(np.fliplr(image)))
                print(sum(t1)/len(t1))
                print(sum(t2)/len(t2))
                print(sum(self.cpu.t1)/len(self.cpu.t1))
                print(sum(self.cpu.t2)/len(self.cpu.t2))
                print(sum(self.cpu.t3)/len(self.cpu.t3))
                print(sum(self.cpu.t4)/len(self.cpu.t4))
                return()
