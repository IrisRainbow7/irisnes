class CPUBus:

    def __init__(self, nes):
        self.nes = nes
        self.ram = [0]*0x800

    def read(self, address):
        if address < 0x800:
            return(self.ram[address])
        elif address < 0x2000:
            return(self.ram[address-0x800])
        elif address <= 0x4000:
            return(self.nes.PPUBus.read((address-0x2000)%8))
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

class PPUBus:

    def __init__(self, nes):
        self.nes = nes
        self.ram = [0]*0x4000

    def read(self, address):
        if address < 8:
            return(self.nes.ppu.registers[address])
        else:
            return(self.ram[address])

    def write(self, address, data):
        if address < 0x0008:
            self.nes.ppu.write(address, data)
        else:
            self.ram[address] = data

    def write_vram(self, address, data):
        self.ram[address] = data

