

class CPU:
    def __init__(self, cassette):
        self.cassette = cassette
        self.set_default_registers()
        self.memory = []
        self.program_memory = self.cassette.program_rom
        self.wram = [0]*0x800

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

    def get_p_register(self):
        p = 0b00000000
        for b,i in enumerate(self.registers['P'].values()):
            if b: p |= (0b1 << (7-i))
        return(p)

    def set_p_register(self, register):
        for b,i in enumerate(bin(register)[2:]):
            self.registers['P'][i] = bool(int(b))


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
            return(self.read(upper_address)*0x100 + self.read(lower_address))
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
        elif address in list(range(0,0x7FF)): #WRAM
            return(self.wram[address])
        elif address in list(range(0x800,0x1FFF)): #WRAMミラー
            return(self.wram[address-0x800])
        else:
            return(0x0000)

    def write(self,address, data):
        if address in list(range(0,0x7FF)): #WRAM
            wram[address] = data
        pass

    def push(self, data):
        self.write(0x100 | self.registers['SP'], data)
        self.registers['SP'] -= 1

    def pop(self):
        self.registers['SP'] +=1
        return(self.read(0x100 | self.registers['SP']))

    def increment_data(self, address):
        if address in list(range(0x8000,0xFFFF)):
            self.program_memory[address-0x8000] += 1
        else:
            pass

    def decrement_data(self, address):
        if address in list(range(0x8000,0xFFFF)):
            self.program_memory[address-0x8000] += 1
        else:
            pass

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
        elif addressing == 'absoluteX': return(self.fetch_word()+self.registers['X'])
        elif addressing == 'absoluteY': return(self.fetch_word()+self.registers['Y'])
        elif addressing == 'preIndexedIndirect':
            address = self.fetch()+self.registers['X']
            return(self.read(address)+self.read(address+1)*0x00)
        elif addressing == 'postIndexedIndirect':
            address = self.fetch()
            return(self.read(address)+self.read(address+1)+self.registers['Y'])
        elif addressing == 'indirectAbsolute':
            address = self.fetch_word()
            return(self.read(address)+self.read(address+1))

    def exec(basename, opeland, mode):
        if basename == 'LDA':
            if mode == 'immediate': self.registers['A'] = opeland
            else: self.registers['A'] = self.read(opeland)
            self.registers['P']['negative'] = self.registers['A'] > 0x80
            self.registers['P']['zero'] = not self.registers['P']['negative']
        if basename == 'LDX':
            if mode == 'immediate': self.registers['X'] = opeland
            else: self.registers['X'] = self.read(opeland)
            self.registers['P']['negative'] = self.registers['X'] > 0x80
            self.registers['P']['zero'] = not self.registers['P']['negative']
        if basename == 'LDY':
            if mode == 'immediate': self.registers['Y'] = opeland
            else: self.registers['Y'] = self.read(opeland)
            self.registers['P']['negative'] = self.registers['A'] > 0x80
            self.registers['P']['zero'] = not self.registers['P']['negative']

        if basename == 'STA':
            self.registers['A'] = opeland
        if basename == 'STX':
            self.registers['X'] = opeland
        if basename == 'STY':
            self.registers['Y'] = opeland

        if basename == 'TAX':
            self.registers['X'] = self.registers['A']
            self.registers['P']['negative'] = self.registers['X'] > 0x80
            self.registers['P']['zero'] = not self.registers['P']['negative']
        if basename == 'TXA':
            self.registers['A'] = self.registers['X']
            self.registers['P']['negative'] = self.registers['A'] > 0x80
            self.registers['P']['zero'] = not self.registers['P']['negative']
        if basename == 'TYA':
            self.registers['A'] = self.registers['Y']
            self.registers['P']['negative'] = self.registers['A'] > 0x80
            self.registers['P']['zero'] = not self.registers['P']['negative']
        if basename == 'TSX':
            self.registers['X'] = self.registers['SP']
            self.registers['P']['negative'] = self.registers['X'] > 0x80
            self.registers['P']['zero'] = not self.registers['P']['negative']
        if basename == 'TXS':
            self.registers['SP'] = self.registers['X']

        if basename == 'ADC':
            if mode == 'immediate':data = opeland
            else: data = self.read(opeland)
            overflow_flag = self.registers['A'] < 0x80
            self.registers['A'] += data + int(self.registers['P']['carry'])
            self.registers['P']['negative'] = self.registers['A'] > 0x80
            self.registers['P']['zero'] = not self.registers['P']['negative']
            self.registers['P']['overflow'] = overflow_flag and self.registers['A'] >= 0x80
            self.registers['P']['carry'] = not overflow_flag and self.registers['A'] >= 0x80
        if basename == 'SBC':
            if mode == 'immediate':data = opeland
            else: data = self.read(opeland)
            overflow_flag = self.registers['A'] < 0x80
            self.registers['A'] -= data + int(not self.registers['P']['carry'])
            self.registers['P']['negative'] = self.registers['A'] > 0x80
            self.registers['P']['zero'] = not self.registers['P']['negative']
            self.registers['P']['overflow'] = overflow_flag and self.registers['A'] >= 0x80
            self.registers['P']['carry'] = not overflow_flag and self.registers['A'] >= 0x80

        if basename == 'AND':
            if mode == 'immediate':data = opeland
            else: data = self.read(opeland)
            self.registers['A'] = self.registers['A'] & data
            self.registers['P']['negative'] = self.registers['A'] > 0x80
            self.registers['P']['zero'] = not self.registers['P']['negative']
        if basename == 'ORA':
            if mode == 'immediate':data = opeland
            else: data = self.read(opeland)
            self.registers['A'] = self.registers['A'] | data
            self.registers['P']['negative'] = self.registers['A'] > 0x80
            self.registers['P']['zero'] = not self.registers['P']['negative']
        if basename == 'EOR':
            if mode == 'immediate':data = opeland
            else: data = self.read(opeland)
            self.registers['A'] = self.registers['A'] ^ data
            self.registers['P']['negative'] = self.registers['A'] > 0x80
            self.registers['P']['zero'] = not self.registers['P']['negative']

        if basename == 'ASL':
            self.registers['A'] = self.registers['A'] << 1
            self.registers['P']['negative'] = self.registers['A'] > 0x80
            self.registers['P']['zero'] = not self.registers['P']['negative']
            self.registers['P']['carry'] = self.registers['A']>=0x80
        if basename == 'LSR':
            self.registers['A'] = self.registers['A'] >> 1
            self.registers['P']['negative'] = self.registers['A'] > 0x80
            self.registers['P']['zero'] = not self.registers['P']['negative']
            self.registers['P']['carry'] = self.registers['A'] % 2 == 1
        if basename == 'ROL':
            self.registers['A'] = self.registers['A'] << 1
            self.registers['A'] += self.registers['P']['carry']
            self.registers['P']['negative'] = self.registers['A'] > 0x80
            self.registers['P']['zero'] = not self.registers['P']['negative']
            self.registers['P']['carry'] = self.registers['A']>=0x80
        if basename == 'ROR':
            self.registers['A'] = self.registers['A'] >> 1
            self.registers['A'] += self.registers['P']['carry'] *0x10
            self.registers['P']['negative'] = self.registers['A'] > 0x80
            self.registers['P']['zero'] = not self.registers['P']['negative']
            self.registers['P']['carry'] = self.registers['A'] % 2 == 1

        if basename == 'BCC':
            if not self.registers['P']['carry']:
                self.registers['PC'] = opeland
            else:
                self.registers['PC'] += 2
        if basename == 'BCS':
            if self.registers['P']['carry']:
                self.registers['PC'] = opeland
            else:
                self.registers['PC'] += 2
        if basename == 'BEQ':
            if self.registers['P']['zero']:
                self.registers['PC'] = opeland
            else:
                self.registers['PC'] += 2
        if basename == 'BNE':
            if not self.registers['P']['zero']:
                self.registers['PC'] = opeland
            else:
                self.registers['PC'] += 2
        if basename == 'BVC':
            if not self.registers['P']['overflow']:
                self.registers['PC'] = opeland
            else:
                self.registers['PC'] += 2
        if basename == 'BVS':
            if self.registers['P']['overflow']:
                self.registers['PC'] = opeland
            else:
                self.registers['PC'] += 2
        if basename == 'BPL':
            if not self.registers['P']['negative']:
                self.registers['PC'] = opeland
            else:
                self.registers['PC'] += 2
        if basename == 'BMI':
            if self.registers['P']['negative']:
                self.registers['PC'] = opeland
            else:
                self.registers['PC'] += 2

        if basename == 'BIT':
            if mode == 'immediate':data = opeland
            else: data = self.read(opeland)
            data = data & self.registers['A']
            self.registers['P']['zero'] = (data == 0)
            self.registers['P']['negative'] = (data & 0b01000000 != 0)
            self.registers['P']['overflow'] = (data & 0b00100000 != 0)

        if basename == 'JMP':
            if mode == 'immediate':data = opeland
            else: data = self.read(opeland)
            self.registers['PC'] = data
        if basename == 'JSR':
             if mode == 'immediate':data = opeland
             else: data = self.read(opeland)
             self.push((self.registers['PC'] & 0xFF00) >> 8)
             self.push(self.registers['PC'] & 0x00FF)
             self.registers['PC'] = data
        if basename == 'RTS':
            self.registers['PC'] = self.pop()*0x100 + self.pop() + 1

        if basename == 'BRK':
            if self.registers['P']['interrupt']: return()
            self.registers['P']['break'] = True
            self.registers['PC'] += 1
            self.push((self.registers['PC'] & 0xFF00) >> 8)
            self.push(self.registers['PC'] & 0x00FF)
            self.push(self.get_p_register())
            self.registers['P']['interrupt'] = True
            self.registers['PC'] = self.read_word(0xFFFE)
        if basename == 'RTI':
            self.set_p_register(self.pop())
            self.registers['PC'] = self.pop()*0x100 + self.pop() + 1

        if basename == 'CMP':
            self.registers['P']['negative'] = self.registers['A']-opeland < 0
            self.registers['P']['zero'] = self.registers['A'] == opeland
            self.registers['P']['carry'] = self.registers['A']-opeland >= 0
        if basename == 'CPX':
            self.registers['P']['negative'] = self.registers['X']-opeland < 0
            self.registers['P']['zero'] = self.registers['X'] == opeland
            self.registers['P']['carry'] = self.registers['X']-opeland >= 0
        if basename == 'CPY':
            self.registers['P']['negative'] = self.registers['Y']-opeland < 0
            self.registers['P']['zero'] = self.registers['Y'] == opeland
            self.registers['P']['carry'] = self.registers['Y']-opeland >= 0

        if basename == 'INC':
            if mode == 'immediate':data = opeland
            else: data = self.read(opeland)
            self.increment_data(data)
        if basename == 'DEC':
            if mode == 'immediate':data = opeland
            else: data = self.read(opeland)
            self.decrement_data(data)
        if basename == 'INX':
            self.registers['X'] += 1
        if basename == 'DEX':
            self.registers['X'] -= 1
        if basename == 'INY':
            self.registers['Y'] += 1
        if basename == 'DEY':
            self.registers['Y'] -= 1

        if basename == 'CLC':
            self.registers['P']['carry'] = False
        if basename == 'SEC':
            self.registers['P']['carry'] = True
        if basename == 'CLI':
            self.registers['P']['interrupt'] = False
        if basename == 'SEI':
            self.registers['P']['interrupt'] = True
        if basename == 'CLD':
            self.registers['P']['decimal'] = False
        if basename == 'SED':
            self.registers['P']['decimal'] = True
        if basename == 'CLV':
            self.registers['P']['overflow'] = False
        if basename == 'PHA':
            self.push(self.registers['A'])
        if basename == 'PLA':
            self.registers['A'] = self.pop()
            self.registers['P']['negative'] = self.registers['A'] < 0
            self.registers['P']['zero'] = self.registers['A'] == 0
        if basename == 'PHP':
            self.push(self.get_p_register())
        if basename == 'PLP':
            self.set_p_register(self.pop())

        if basename == 'NOP':
            pass























