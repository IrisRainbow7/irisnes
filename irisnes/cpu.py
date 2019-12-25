

class CPU:
    def __init__(self, cassette):
        self.cassette = cassette
        self.set_default_registers()
        self.memory = []
        self.program_memory = self.cassette.program_rom

    def set_default_registers(self):
        self.registers = {
                          'A': 0x00,
                          'X': 0x00,
                          'Y': 0x00,
                          'P': {
                                'negative': False,
                                'overflow': False,
                                'reserved': True,
                                'break': True,
                                'decimal': False,
                                'interrupt': True,
                                'zero': False,
                                'carry': False
                                },
                          'SP': 0x01FD,  # Stack Pointer
                          'PC': 0x0000,  # Program Counter
                          }

    def reset(self):
        self.set_default_registers()
        self.registers['PC'] = self.read_word(0xFFFC)

    def read_word(self, address):
        """
        ２バイト読み込み
        """
        if address in list(range(0x8000,0xFFFF)):
            lower_address = address - 0x8000
            upper_address = lower_address + 1
            return(self.program_memory[upper_address]*0x100 + self.program_memory[lower_address])
        else:
            return(0x0000)

    def fetch_word(self):
        self.registers['PC'] += 1
        upper = self.read(self.registers['PC']-1)
        self.registers['PC'] += 1
        lower = self.read(self.registers['PC']-1)
        return(upper*0x100 + lower)

    def read(self, address):
        if address in list(range(0x8000,0xFFFF)):
            return(self.program_memory[address-0x8000])
        else:
            return(0x0000)

    def fetch(self):
        self.registers['PC'] += 1
        return(self.read(self.registers['PC']-1))

    def fetch_opeland(self, addressing):
        if addressing == 'accumulator': return()
        elif addressing == 'implied': return()
        elif addressing == 'immediate': return(self.fetch())
        elif addressing == 'zeroPage': return(self.fetch()*0x100)
        elif addressing == 'zeroPageX': return((self.fetch()+self.registers['X'])*0x00)
        elif addressing == 'zeroPageY': return((self.fetch()+self.registers['Y'])*0x00)
        elif addressing == 'absolute': return(self.fetch_word())
