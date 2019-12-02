

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
        if address in list(range(0x8000,0xFFFF)):
            return(self.program_memory[address-0x8000])
        else:
            return(0x0000)

