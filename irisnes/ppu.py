import irisnes
import numpy as np

class PPU:

    COLORS = [
              [0x80, 0x80, 0x80], [0x00, 0x3D, 0xA6], [0x00, 0x12, 0xB0], [0x44, 0x00, 0x96],
              [0xA1, 0x00, 0x5E], [0xC7, 0x00, 0x28], [0xBA, 0x06, 0x00], [0x8C, 0x17, 0x00],
              [0x5C, 0x2F, 0x00], [0x10, 0x45, 0x00], [0x05, 0x4A, 0x00], [0x00, 0x47, 0x2E],
              [0x00, 0x41, 0x66], [0x00, 0x00, 0x00], [0x05, 0x05, 0x05], [0x05, 0x05, 0x05],
              [0xC7, 0xC7, 0xC7], [0x00, 0x77, 0xFF], [0x21, 0x55, 0xFF], [0x82, 0x37, 0xFA],
              [0xEB, 0x2F, 0xB5], [0xFF, 0x29, 0x50], [0xFF, 0x22, 0x00], [0xD6, 0x32, 0x00],
              [0xC4, 0x62, 0x00], [0x35, 0x80, 0x00], [0x05, 0x8F, 0x00], [0x00, 0x8A, 0x55],
              [0x00, 0x99, 0xCC], [0x21, 0x21, 0x21], [0x09, 0x09, 0x09], [0x09, 0x09, 0x09],
              [0xFF, 0xFF, 0xFF], [0x0F, 0xD7, 0xFF], [0x69, 0xA2, 0xFF], [0xD4, 0x80, 0xFF],
              [0xFF, 0x45, 0xF3], [0xFF, 0x61, 0x8B], [0xFF, 0x88, 0x33], [0xFF, 0x9C, 0x12],
              [0xFA, 0xBC, 0x20], [0x9F, 0xE3, 0x0E], [0x2B, 0xF0, 0x35], [0x0C, 0xF0, 0xA4],
              [0x05, 0xFB, 0xFF], [0x5E, 0x5E, 0x5E], [0x0D, 0x0D, 0x0D], [0x0D, 0x0D, 0x0D],
              [0xFF, 0xFF, 0xFF], [0xA6, 0xFC, 0xFF], [0xB3, 0xEC, 0xFF], [0xDA, 0xAB, 0xEB],
              [0xFF, 0xA8, 0xF9], [0xFF, 0xAB, 0xB3], [0xFF, 0xD2, 0xB0], [0xFF, 0xEF, 0xA6],
              [0xFF, 0xF7, 0x9C], [0xD7, 0xE8, 0x95], [0xA6, 0xED, 0xAF], [0xA2, 0xF2, 0xDA],
              [0x99, 0xFF, 0xFC], [0xDD, 0xDD, 0xDD], [0x11, 0x11, 0x11], [0x11, 0x11, 0x11],
            ]

    def __init__(self, nes):
        self.nes = nes
        self.bus = self.nes.ppu_bus
        self.cycle = 0
        self.line = 0
        self.background = []
        self.registers = [0] * 8
        self.building_line = 0
        self.sprite_ram_address = 0
        self.is_lower_vram_address = False
        self.vram_address = 0x0000
        self.vram_offset = 1



    def run(self, cycle):
        self.cycle += cycle
        if self.line == 0:
            self.background = []
            self.building_line = 0

        if self.cycle >= 341:
            self.cycle -= 341
            self.line += 1
            #print('===========line:'+str(self.line)+'=========')

        if self.line <= 240 and self.line % 8 == 0:
            if self.building_line != self.line:
                self.building_line = self.line
                self.build_background()

        if self.line == 262:
            self.line = 0
            self.background = np.vstack(self.background)
            return(self.background)

        return([])


    def build_background(self):
        tile_y = self.line // 8
        tile_x = 0
        data = []
        for tile_x in range(256//8):
            name_table_address = 0x2000 + tile_y*32 + tile_x
            attr_table_y = tile_y // 4
            attr_table_x = tile_x // 4
            attr_table_inner_y = attr_table_y // 2
            attr_table_inner_x = attr_table_x // 2
            attr_table_index = (attr_table_inner_x % 2) + (attr_table_inner_y % 2)*2
            attr_table_data = (0x23C0 + attr_table_y*16 + attr_table_x)
            palette_id = (attr_table_data & (0b11 << (attr_table_index*2))) >> (attr_table_index*2)
            sprite_number = self.bus.read(name_table_address)
            tile = self.nes.cassette.sprite(sprite_number)
            palette_address = 0x3F00 + palette_id*4
            palette_number = self.bus.read(palette_address)
            for i in range(len(tile)):
                for j in range(len(tile[0])):
                    tile[i][j] = np.array(self.COLORS[palette_number])*tile[i][j]
            data.append(tile)
        lines = np.hstack(data)
        self.background.append(lines)


    def write(self, address, data):
        if address == 0x0003:
            self.write_sprite_ram_address(data)
        elif address == 0x0004:
            self.write_sprite_ram_data(data)
        elif address == 0x0005:
            self.write_scroll_data(data)
        elif address == 0x0006:
            self.write_vram_address(data)
        elif address == 0x0007:
            self.write_vram_data(data)
        else:
            self.registers[address] = data

    def write_sprite_ram_address(self, data):
        self.sprite_ram_address = data

    def write_sprite_ram_data(self, data):
        self.nes.bus.write_vram(self.sprite_ram_address, data)
        self.sprite_ram_address += 1

    def write_scroll_data(self, data):
        #TODO
        pass

    def write_vram_address(self, data):
        if self.is_lower_vram_address:
            self.vram_address += data
            self.is_lower_vram_address = False
        else:
            self.vram_address = data << 8
            self.is_lower_vram_address = True

    def write_vram_data(self, data):
        #print(str(hex(self.vram_address))+'=>'+str(hex(data)))
        self.bus.write_vram(self.vram_address, data)
        self.vram_address += self.vram_offset



