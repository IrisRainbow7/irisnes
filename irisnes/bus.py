class CPUBus:

    def __init__(self, nes):
        self.nes = nes
        self.ram = [0]*0x800
        self.write_buffer = 0x00
        self.reading_status = 0
        self.controller_status = [False]*8

    def reset_reading_status(self):
        #print('!!!!')
        self.reading_status = 0
        self.controller_status = list(self.nes.key_status.values())

    def read(self, address):
        if address < 0x800:
            return(self.ram[address])
        elif address < 0x2000:
            return(self.ram[address-0x800])
        elif address < 0x4000:
            return(self.nes.ppu_bus.read((address-0x2000)%8))
        elif address == 0x4016:
            #print('key read')
            self.reading_status += 1
            return(self.controller_status[self.reading_status-1])
        elif address >= 0xC000:
            if len(self.nes.cassette.program_rom) <= 0x4000:
                return(self.nes.cassette.program_rom[address-0xC000])
            else:
                return(self.nes.cassette.program_rom[address-0x8000])
        elif address >= 0x8000:
            return(self.nes.cassette.program_rom[address-0x8000])
        else:
            return(0)

    def write(self, address, data):
        if address < 0x800:
            self.ram[address] = data
        elif address < 0x2000:
            self.ram[address-0x800] = data
        elif address < 0x2008:
            self.nes.ppu_bus.write(address-0x2000, data)
        elif address == 0x4014:
            self.nes.dma_start(data)
        elif address == 0x4016:
            if self.write_buffer == 0x1 and data == 0x0:
                self.reset_reading_status()
            self.write_buffer = data

    def increment_data(self, address):
        if address <= 0x7FF: #WRAM
            self.ram[address] += 1
            self.ram[address] &= 0xFF
        elif 0x800 <= address and address <= 0x1FFF: #WRAMミラー
            self.ram[address-0x800] += 1
            self.ram[address-0x800] &= 0xFF
        else:
            pass

    def decrement_data(self, address):
        if address <= 0x7FF: #WRAM
            self.ram[address] -= 1
            if self.ram[address]< 0:self.ram[address]=0xFF+self.ram[address]+1
        elif 0x800 <= address and address <= 0x1FFF: #WRAMミラー
            self.ram[address-0x800] -= 1
            if self.ram[address-0x800]< 0:self.ram[address-0x800]=0xFF+self.ram[address-0x800]+1
        else:
            pass



class PPUBus:

    def __init__(self, nes):
        self.nes = nes
        self.ram = [0]*0x4000

    def read(self, address):
        if address < 8:
            return(self.nes.ppu.read(address))
        else:
            return(self.ram[address])

    def read_palette(self, address):
        if 0x3F00 <= address and address <= 0x3F1F:
            return(self.ram[address:address+4])
        else:
            raise RuntimeError('address "{}" is not palette address ')

    def write(self, address, data):
        if address < 0x0008:
            self.nes.ppu.write(address, data)
        else:
            self.ram[address] = data

    def write_vram(self, address, data):
        self.ram[address] = data

