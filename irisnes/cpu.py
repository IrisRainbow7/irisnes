import time

class CPU:
    def __init__(self, nes):
        self.nes = nes
        self.bus = self.nes.cpu_bus
        #self.program_memory = self.nes.cassette.program_rom
        self.reset()
        self.t1=[]
        self.t2=[]
        self.t3=[]
        self.t4=[]


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
        for i,b in enumerate(self.registers['P'].values()):
            if b:
                p |= (0b1 << (7-i))
        return(p)

    def set_p_register(self, register):
        keys =['negative','overflow','reserved','break','decimal','interrupt','zero','carry']
        for i,b in enumerate(bin(register)[2:].zfill(8)):
            self.registers['P'][keys[i]] = bool(int(b))
        self.registers['P']['reserved'] = True


    def reset(self):
        self.set_default_registers()
        self.registers['PC'] = self.read_word(0xFFFC)

    def read_word(self, address):
        """
        ２バイト読み込み
        """
        if 0x8000 <= address and address <= 0xFFFF:
            lower_address = address
            upper_address = lower_address + 1
            return(self.read(upper_address)*0x100 + self.read(lower_address))
        else:
            return(0x0000)

    def fetch_word(self):
        lower = self.read(self.registers['PC'])
        self.registers['PC'] += 1
        upper = self.read(self.registers['PC'])
        self.registers['PC'] += 1
        return(upper*0x100 + lower)

    def read(self, address):
        return(self.bus.read(address))

    def write(self, address, data):
        self.bus.write(address, data)

    def push(self, data):
        self.write(0x100 | self.registers['SP'], data)
        #print('\npush: '+hex(data))
        self.registers['SP'] -= 1

    def pop(self):
        self.registers['SP'] +=1
        #print('\npop: '+hex(self.read(0x100 | self.registers['SP'])))
        return(self.read(0x100 | self.registers['SP']))

    def increment_data(self, address):
        self.bus.increment_data(address)

    def decrement_data(self, address):
        self.bus.decrement_data(address)

    def fetch(self):
        self.registers['PC'] += 1
        return(self.read(self.registers['PC']-1))

    def fetch_opeland(self, addressing):
        if addressing == 'accumulator': return(0xFFFFFFFF)
        elif addressing == 'implied': return(0xFFFFFFFF)
        elif addressing == 'immediate': return(self.fetch())
        elif addressing == 'zeroPage': return(self.fetch())
        elif addressing == 'zeroPageX': return((self.fetch()+self.registers['X'])&0xFF)
        elif addressing == 'zeroPageY': return((self.fetch()+self.registers['Y'])&0xFF)
        elif addressing == 'absolute': return(self.fetch_word())
        elif addressing == 'absoluteX': return((self.fetch_word()+self.registers['X'])&0xFFFF)
        elif addressing == 'absoluteY': return((self.fetch_word()+self.registers['Y'])&0xFFFF)
        elif addressing == 'relative': return(self.fetch())
        elif addressing == 'preIndexedIndirect':
            address = (self.fetch()+self.registers['X'])&0xFF
            return(self.read(address)+self.read((address+1)&0xFF)*0x100)
        elif addressing == 'postIndexedIndirect':
            address = self.fetch()
            return((self.read(address)+self.read((address+1)&0xFF)*0x100+self.registers['Y'])&0xFFFF)
        elif addressing == 'indirectAbsolute':
            address = self.fetch_word()
            lower = self.read(address)
            upper_address = (address>>8<<8)+(((address&0xFF)+1)&0xFF)
            upper = self.read(upper_address)<<8
            return(lower+upper)

    def convert_from_two_complement(self, bits):
        if bits < 128:
            decimal = bits
        else:
            decimal = -1*(int(''.join([{'1':'0','0':'1'}[i] for i in bin(bits)[2:]]),2)+1)
        return(decimal)

    def exec(self, basename, opeland, mode):
        #print(basename+','+mode+' => '+opeland)
        if basename == 'LDA':
            if mode == 'immediate': self.registers['A'] = opeland
            else: self.registers['A'] = self.read(opeland)
            self.registers['P']['negative'] = self.registers['A'] >= 0x80
            self.registers['P']['zero'] = self.registers['A'] == 0
        if basename == 'LDX':
            if mode == 'immediate': self.registers['X'] = opeland
            else: self.registers['X'] = self.read(opeland)
            self.registers['P']['negative'] = self.registers['X'] >= 0x80
            self.registers['P']['zero'] = self.registers['X'] == 0
        if basename == 'LDY':
            if mode == 'immediate': self.registers['Y'] = opeland
            else: self.registers['Y'] = self.read(opeland)
            self.registers['P']['negative'] = self.registers['Y'] >= 0x80
            self.registers['P']['zero'] = self.registers['Y'] == 0

        if basename == 'LAX': #Unofficial
            if mode == 'immediate': data = opeland
            else: data = self.read(opeland)
            self.registers['A'] = data
            self.registers['X'] = data
            self.registers['P']['negative'] = self.registers['A'] >= 0x80
            self.registers['P']['zero'] = self.registers['A'] == 0

        if basename == 'STA':
            self.write(opeland, self.registers['A'])
        if basename == 'STX':
            self.write(opeland, self.registers['X'])
        if basename == 'STY':
            self.write(opeland, self.registers['Y'])

        if basename == 'SAX': #Unofficial
            self.write(opeland, self.registers['A'] & self.registers['X'])

        if basename == 'TAX':
            self.registers['X'] = self.registers['A']
            self.registers['P']['negative'] = self.registers['X'] >= 0x80
            self.registers['P']['zero'] = self.registers['X']==0
        if basename == 'TXA':
            self.registers['A'] = self.registers['X']
            self.registers['P']['negative'] = self.registers['A'] >= 0x80
            self.registers['P']['zero'] = self.registers['A']==0
        if basename == 'TAY':
            self.registers['Y'] = self.registers['A']
            self.registers['P']['negative'] = self.registers['Y'] >= 0x80
            self.registers['P']['zero'] = self.registers['Y']==0
        if basename == 'TYA':
            self.registers['A'] = self.registers['Y']
            self.registers['P']['negative'] = self.registers['A'] >= 0x80
            self.registers['P']['zero'] = self.registers['A']==0
        if basename == 'TSX':
            self.registers['X'] = self.registers['SP']
            self.registers['P']['negative'] = self.registers['X'] >= 0x80
            self.registers['P']['zero'] = self.registers['X']==0
        if basename == 'TXS':
            self.registers['SP'] = self.registers['X']+0x0100

        if basename == 'ADC':
            if mode == 'immediate': data = opeland
            else: data = self.read(opeland)
            carry_flag = (self.registers['A'] + data + int(self.registers['P']['carry']))>0xFF
            overflow_flag = not (-128 <= (self.convert_from_two_complement(self.registers['A'])+self.convert_from_two_complement(data)+int(self.registers['P']['carry'])) <= 127)
            self.registers['A'] += data + int(self.registers['P']['carry'])
            self.registers['A'] &= 0xFF
            self.registers['P']['negative'] = self.registers['A'] >= 0x80
            self.registers['P']['zero'] = self.registers['A'] == 0
            self.registers['P']['carry'] = carry_flag
            self.registers['P']['overflow'] = overflow_flag
        if basename == 'SBC':
            if mode == 'immediate': data = opeland
            else: data = self.read(opeland)
            carry_flag = 0<=(self.registers['A'] - data - int(not self.registers['P']['carry']))<=0xFF
            overflow_flag = not (-128 <= (self.convert_from_two_complement(self.registers['A'])-self.convert_from_two_complement(data)-int(not self.registers['P']['carry'])) <= 127)
            self.registers['A'] -= data + int(not self.registers['P']['carry'])
            if self.registers['A'] < 0:self.registers['A']=0xFF+self.registers['A']+1
            self.registers['P']['negative'] = self.registers['A'] >= 0x80
            self.registers['P']['zero'] = self.registers['A'] == 0
            self.registers['P']['overflow'] = overflow_flag
            self.registers['P']['carry'] = carry_flag

        if basename == 'AND':
            if mode == 'immediate': data = opeland
            else: data = self.read(opeland)
            self.registers['A'] = self.registers['A'] & data
            self.registers['P']['negative'] = self.registers['A'] >= 0x80
            self.registers['P']['zero'] = self.registers['A']==0
        if basename == 'ORA':
            if mode == 'immediate': data = opeland
            else: data = self.read(opeland)
            self.registers['A'] = self.registers['A'] | data
            self.registers['P']['negative'] = self.registers['A'] >= 0x80
            self.registers['P']['zero'] = self.registers['A']==0
        if basename == 'EOR':
            if mode == 'immediate': data = opeland
            else: data = self.read(opeland)
            self.registers['A'] = self.registers['A'] ^ data
            self.registers['P']['negative'] = self.registers['A'] >= 0x80
            self.registers['P']['zero'] = self.registers['A']==0

        if basename == 'ALR':
            data = opeland
            self.registers['A'] = self.registers['A'] & data
            self.registers['P']['negative'] = self.registers['A'] >= 0x80
            self.registers['P']['zero'] = self.registers['A']==0
            self.registers['P']['carry'] = self.registers['A'] % 2 == 1
            self.registers['A'] = self.registers['A'] >> 1
            self.registers['P']['negative'] = self.registers['A'] >= 0x80
            self.registers['P']['zero'] = self.registers['A']==0
        if basename == 'ANC':
            data = opeland
            self.registers['A'] = self.registers['A'] & data
            self.registers['P']['negative'] = self.registers['A'] >= 0x80
            self.registers['P']['zero'] = self.registers['A']==0
            self.registers['P']['carry'] = self.registers['P']['negative']
        if basename == 'ARR':
            data = opeland
            self.registers['A'] = self.registers['A'] & data
            self.registers['P']['negative'] = self.registers['A'] >= 0x80
            self.registers['P']['zero'] = self.registers['A']==0
            self.registers['A'] = self.registers['A'] >> 1
            self.registers['A'] += (int(self.registers['P']['carry']) << 7)
            self.registers['P']['negative'] = self.registers['A'] >= 0x80
            self.registers['P']['zero'] = self.registers['A']==0
            self.registers['P']['carry'] = (self.registers['A']&0b1000000) != 0
            self.registers['P']['overflow'] = int((self.registers['A']&0b1000000)!=0)^int((self.registers['A']&0b100000)!=0)
        if basename == 'AXS':
            self.registers['X'] = (self.registers['A']&self.registers['X'])-opeland
            self.registers['P']['negative'] = self.registers['X'] >= 0x80
            self.registers['P']['zero'] = self.registers['X']==0
            self.registers['P']['carry'] = self.registers['X']>=0x80

        if basename == 'ASL':
            if mode == 'accumulator':
                self.registers['P']['carry'] = self.registers['A']>=0x80
                self.registers['A'] = self.registers['A'] << 1
                self.registers['A'] &= 0xFF
                self.registers['P']['negative'] = self.registers['A'] >= 0x80
                self.registers['P']['zero'] = self.registers['A']==0
            else:
                data = self.read(opeland)
                self.registers['P']['carry'] = data>=0x80
                data = data << 1
                data &= 0xFF
                self.write(opeland, data)
                self.registers['P']['negative'] = data >= 0x80
                self.registers['P']['zero'] = data==0
        if basename == 'LSR':
            if mode == 'accumulator':
                self.registers['P']['carry'] = self.registers['A'] % 2 == 1
                self.registers['A'] = self.registers['A'] >> 1
                self.registers['P']['negative'] = self.registers['A'] >= 0x80
                self.registers['P']['zero'] = self.registers['A']==0
            else:
                data = self.read(opeland)
                self.registers['P']['carry'] = data % 2 == 1
                data = data >> 1
                self.write(opeland,data)
                self.registers['P']['negative'] = data >= 0x80
                self.registers['P']['zero'] = data==0
        if basename == 'ROL':
            if mode == 'accumulator':
                carry_flag = self.registers['A']>=0x80
                self.registers['A'] = self.registers['A'] << 1
                self.registers['A'] += int(self.registers['P']['carry'])
                self.registers['A'] &= 0xFF
                self.registers['P']['negative'] = self.registers['A'] >= 0x80
                self.registers['P']['zero'] = self.registers['A']==0
                self.registers['P']['carry'] = carry_flag
            else:
                data = self.read(opeland)
                carry_flag = data>=0x80
                data = data << 1
                data += int(self.registers['P']['carry'])
                data &= 0xFF
                self.write(opeland,data)
                self.registers['P']['negative'] = data >= 0x80
                self.registers['P']['zero'] = data==0
                self.registers['P']['carry'] = carry_flag
        if basename == 'ROR':
            if mode == 'accumulator':
                carry_flag = self.registers['A'] % 2 == 1
                self.registers['A'] = self.registers['A'] >> 1
                self.registers['A'] += (int(self.registers['P']['carry']) << 7)
                self.registers['P']['negative'] = self.registers['A'] >= 0x80
                self.registers['P']['zero'] = self.registers['A']==0
                self.registers['P']['carry'] = carry_flag
            else:
                data = self.read(opeland)
                carry_flag = data % 2 == 1
                data = data >> 1
                data += (int(self.registers['P']['carry']) << 7)
                self.write(opeland,data)
                self.registers['P']['negative'] = data >= 0x80
                self.registers['P']['zero'] = data==0
                self.registers['P']['carry'] = carry_flag

        if basename == 'SLO':
            data = self.read(opeland)
            self.registers['P']['carry'] = data>=0x80
            data = data << 1
            data &= 0xFF
            self.registers['A'] |= data
            self.registers['P']['negative'] = self.registers['A'] >= 0x80
            self.registers['P']['zero'] = self.registers['A']==0
            self.write(opeland, data)
        if basename == 'SRE':
            data = self.read(opeland)
            self.registers['P']['carry'] = data % 2 == 1
            data = data >> 1
            self.registers['A'] = self.registers['A']^data
            self.registers['P']['negative'] = self.registers['A'] >= 0x80
            self.registers['P']['zero'] = self.registers['A']==0
            self.write(opeland,data)
        if basename == 'RLA':
            data = self.read(opeland)
            carry_flag = data>=0x80
            data = data << 1
            data += int(self.registers['P']['carry'])
            data &= 0xFF
            self.registers['A'] = (self.registers['A'] & data) & 0xFF
            self.registers['P']['negative'] = self.registers['A'] >= 0x80
            self.registers['P']['zero'] = self.registers['A']==0
            self.registers['P']['carry'] = carry_flag
            self.write(opeland,data)
        if basename == 'RRA':
            data = self.read(opeland)
            carry_flag = data % 2 == 1
            data = data >> 1
            data += (int(self.registers['P']['carry']) << 7)
            overflow_flag = not (-128 <= (self.convert_from_two_complement(self.registers['A'])+self.convert_from_two_complement(data)+int(self.registers['P']['carry'])) <= 127)
            self.registers['P']['carry'] = carry_flag
            carry_flag = (self.registers['A'] + data + int(self.registers['P']['carry']))>0xFF
            self.registers['A'] += data + int(self.registers['P']['carry'])
            self.registers['A'] &= 0xFF
            self.registers['P']['negative'] = self.registers['A'] >= 0x80
            self.registers['P']['zero'] = self.registers['A'] == 0
            self.registers['P']['overflow'] = overflow_flag
            self.registers['P']['carry'] = carry_flag
            self.write(opeland,data)

        if basename == 'BCC':
            if not self.registers['P']['carry']:
                self.registers['PC'] += self.convert_from_two_complement(opeland)
        if basename == 'BCS':
            if self.registers['P']['carry']:
                self.registers['PC'] += self.convert_from_two_complement(opeland)
        if basename == 'BEQ':
            if self.registers['P']['zero']:
                self.registers['PC'] += self.convert_from_two_complement(opeland)
        if basename == 'BNE':
            if not self.registers['P']['zero']:
                self.registers['PC'] += self.convert_from_two_complement(opeland)
        if basename == 'BVC':
            if not self.registers['P']['overflow']:
                self.registers['PC'] += self.convert_from_two_complement(opeland)
        if basename == 'BVS':
            if self.registers['P']['overflow']:
                self.registers['PC'] += self.convert_from_two_complement(opeland)
        if basename == 'BPL':
            if not self.registers['P']['negative']:
                self.registers['PC'] += self.convert_from_two_complement(opeland)
        if basename == 'BMI':
            if self.registers['P']['negative']:
                self.registers['PC'] += self.convert_from_two_complement(opeland)

        if basename == 'BIT':
            data = self.read(opeland)
            self.registers['P']['zero'] = ((data & self.registers['A']) == 0)
            self.registers['P']['negative'] = (data & 0b10000000 != 0)
            self.registers['P']['overflow'] = (data & 0b01000000 != 0)

        if basename == 'JMP':
            self.registers['PC'] = opeland
        if basename == 'JSR':
            if mode == 'immediate'or'absolute': data = opeland
            else: data = self.read(opeland)
            self.push(((self.registers['PC']-1) & 0xFF00) >> 8)
            self.push((self.registers['PC']-1) & 0x00FF)
            self.registers['PC'] = data
        if basename == 'RTS':
            self.registers['PC'] = self.pop() + (self.pop()<<8) + 1

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
            self.registers['PC'] = self.pop() + (self.pop()<<8)

        if basename == 'CMP':
            if mode == 'immediate': data = opeland
            else: data = self.read(opeland)
            self.registers['P']['negative'] = (self.registers['A']-data) >= 0x80 or self.registers['A']-data < 0
            self.registers['P']['zero'] = self.registers['A'] == data
            self.registers['P']['carry'] = self.registers['A']-data >= 0
        if basename == 'CPX':
            if mode == 'immediate': data = opeland
            else: data = self.read(opeland)
            self.registers['P']['negative'] = (self.registers['X']-data) >= 0x80 or self.registers['X']-data < 0
            self.registers['P']['zero'] = self.registers['X'] == data
            self.registers['P']['carry'] = self.registers['X']-data >= 0
        if basename == 'CPY':
            if mode == 'immediate': data = opeland
            else: data = self.read(opeland)
            self.registers['P']['negative'] = (self.registers['Y']-data) >= 0x80 or self.registers['Y']-data < 0
            self.registers['P']['zero'] = self.registers['Y'] == data
            self.registers['P']['carry'] = self.registers['Y']-data >= 0

        if basename == 'INC':
            self.increment_data(opeland)
            data = self.read(opeland)
            self.registers['P']['negative'] = (data)&0xFF >= 0x80
            self.registers['P']['zero'] = (data)&0xFF == 0
        if basename == 'DEC':
            self.decrement_data(opeland)
            data = self.read(opeland)
            self.registers['P']['negative'] = (data & 0b10000000) != 0
            self.registers['P']['zero'] = data == 0
        if basename == 'INX':
            self.registers['X'] += 1
            self.registers['X'] &= 0xFF
            self.registers['P']['negative'] = (self.registers['X'] & 0b10000000) != 0
            self.registers['P']['zero'] = self.registers['X'] == 0
        if basename == 'DEX':
            self.registers['X'] -= 1
            if self.registers['X'] < 0:self.registers['X']=0xFF+self.registers['X']+1
            self.registers['P']['negative'] = (self.registers['X']  & 0b10000000) != 0
            self.registers['P']['zero'] = self.registers['X'] == 0
        if basename == 'INY':
            self.registers['Y'] += 1
            self.registers['Y'] &= 0xFF
            self.registers['P']['negative'] = (self.registers['Y']  & 0b10000000) != 0
            self.registers['P']['zero'] = self.registers['Y'] == 0
        if basename == 'DEY':
            self.registers['Y'] -= 1
            if self.registers['Y'] < 0:self.registers['Y']=0xFF+self.registers['Y']+1
            self.registers['P']['negative'] = (self.registers['Y']  & 0b10000000) != 0
            self.registers['P']['zero'] = self.registers['Y'] == 0

        if basename == 'DCP':
            self.decrement_data(opeland)
            data = self.read(opeland)
            if self.registers['A']-data<0:
                self.registers['P']['negative'] = (0xFF+self.registers['A']+data)&0xFF >= 0x80
            else:
                self.registers['P']['negative'] = self.registers['A']-data >= 0x80
            self.registers['P']['zero'] = self.registers['A']-data == 0

        if basename == 'ISB':
            self.increment_data(opeland)
            data = self.read(opeland)
            carry_flag = 0<=(self.registers['A'] - data - int(not self.registers['P']['carry']))<=0xFF
            overflow_flag = not (-128 <= (self.convert_from_two_complement(self.registers['A'])-self.convert_from_two_complement(data)-int(not self.registers['P']['carry'])) <= 127)
            self.registers['A'] -= data + int(not self.registers['P']['carry'])
            if self.registers['A'] < 0:self.registers['A']=0xFF+self.registers['A']+1
            self.registers['P']['negative'] = self.registers['A'] >= 0x80
            self.registers['P']['zero'] = self.registers['A'] == 0
            self.registers['P']['overflow'] = overflow_flag
            self.registers['P']['carry'] = carry_flag

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
            self.registers['P']['negative'] = self.registers['A'] >= 0x80
            self.registers['P']['zero'] = self.registers['A'] == 0
        if basename == 'PHP':
            self.push(self.get_p_register())
        if basename == 'PLP':
            break_flag = self.registers['P']['break']
            self.set_p_register(self.pop())
            self.registers['P']['reserved'] = True
            self.registers['P']['break'] = break_flag

        if basename == 'NOP':
            pass


    OPECODE_LIST = [
                    ['BRK','implied',7],['ORA','preIndexedIndirect',6],['NOP','implied',2],['SLO','preIndexedIndirect',8],['NOP','zeroPage',3],['ORA','zeroPage',3],['ASL','zeroPage',5],['SLO','zeroPage',5],['PHP','implied',3],['ORA','immediate',2],['ASL','accumulator',2],['ANC','immediate',2],['NOP','absolute',4],['ORA','absolute',4],['ASL','absolute',6],['SLO','absolute',6],
                    ['BPL','relative',2],['ORA','postIndexedIndirect',5],['NOP','implied',2],['SLO','postIndexedIndirect',8],['NOP','zeroPageX',4],['ORA','zeroPageX',4],['ASL','zeroPageX',6],['SLO','zeroPageX',6],['CLC','implied',2],['ORA','absoluteY',4],['NOP','implied',2],['SLO','absoluteY',7],['NOP','absoluteX',4],['ORA','absoluteX',4],['ASL','absoluteX',6],['SLO','absoluteX',7],
                    ['JSR','absolute',6],['AND','preIndexedIndirect',6],['NOP','implied',2],['RLA','preIndexedIndirect',8],['BIT','zeroPage',3],['AND','zeroPage',3],['ROL','zeroPage',5],['RLA','zeroPage',5],['PLP','implied',4],['AND','immediate',2],['ROL','accumulator',2],['ANC','immediate',2],['BIT','absolute',4],['AND','absolute',4],['ROL','absolute',6],['RLA','absolute',6],
                    ['BMI','relative',2],['AND','postIndexedIndirect',5],['NOP','implied',2],['RLA','postIndexedIndirect',8],['NOP','zeroPageX',4],['AND','zeroPageX',4],['ROL','zeroPageX',6],['RLA','zeroPageX',6],['SEC','implied',2],['AND','absoluteY',4],['NOP','implied',2],['RLA','absoluteY',7],['NOP','absoluteX',4],['AND','absoluteX',4],['ROL','absoluteX',6],['RLA','absoluteX',7],
                    ['RTI','implied',6],['EOR','preIndexedIndirect',6],['NOP','implied',2],['SRE','preIndexedIndirect',8],['NOP','zeroPage',4],['EOR','zeroPage',3],['LSR','zeroPage',5],['SRE','zeroPage',5],['PHA','implied',3],['EOR','immediate',2],['LSR','accumulator',2],['ALR','immediate',2],['JMP','absolute',3],['EOR','absolute',4],['LSR','absolute',6],['SRE','absolute',6],
                    ['BVC','relative',2],['EOR','postIndexedIndirect',5],['NOP','implied',2],['SRE','postIndexedIndirect',8],['NOP','zeroPageX',4],['EOR','zeroPageX',4],['LSR','zeroPageX',6],['SRE','zeroPageX',6],['CLI','implied',2],['EOR','absoluteY',4],['NOP','implied',2],['SRE','absoluteY',7],['NOP','absoluteX',4],['EOR','absoluteX',4],['LSR','absoluteX',6],['SRE','absoluteX',7],
                    ['RTS','implied',6],['ADC','preIndexedIndirect',6],['NOP','implied',2],['RRA','preIndexedIndirect',8],['NOP','zeroPage',3],['ADC','zeroPage',3],['ROR','zeroPage',5],['RRA','zeroPage',5],['PLA','implied',4],['ADC','immediate',2],['ROR','accumulator',2],['ARR','immediate',2],['JMP','indirectAbsolute',5],['ADC','absolute',4],['ROR','absolute',6],['RRA','absolute',6],
                    ['BVS','relative',2],['ADC','postIndexedIndirect',5],['NOP','implied',2],['RRA','postIndexedIndirect',8],['NOP','zeroPageX',4],['ADC','zeroPageX',4],['ROR','zeroPageX',6],['RRA','zeroPageX',6],['SEI','implied',2],['ADC','absoluteY',4],['NOP','implied',2],['RRA','absoluteY',7],['NOP','absoluteX',4],['ADC','absoluteX',4],['ROR','absoluteX',6],['RRA','absoluteX',7],
                    ['NOP','immediate',2],['STA','preIndexedIndirect',6],['NOP','implied',2],['SAX','preIndexedIndirect',6],['STY','zeroPage',3],['STA','zeroPage',3],['STX','zeroPage',3],['SAX','zeroPage',3],['DEY','implied',2],['NOP','implied',2],['TXA','implied',2],['NOP','implied',2],['STY','absolute',4],['STA','absolute',4],['STX','absolute',4],['SAX','absolute',4],
                    ['BCC','relative',2],['STA','postIndexedIndirect',6],['NOP','implied',2],['NOP','implied',6],['STY','zeroPageX',4],['STA','zeroPageX',4],['STX','zeroPageY',4],['SAX','zeroPageY',4],['TYA','implied',2],['STA','absoluteY',4],['TXS','implied',2],['NOP','implied',5],['NOP','implied',5],['STA','absoluteX',4],['NOP','implied',5],['NOP','implied',5],
                    ['LDY','immediate',2],['LDA','preIndexedIndirect',6],['LDX','immediate',2],['LAX','preIndexedIndirect',6],['LDY','zeroPage',3],['LDA','zeroPage',3],['LDX','zeroPage',3],['LAX','zeroPage',3],['TAY','implied',2],['LDA','immediate',2],['TAX','implied',2],['NOP','implied',2],['LDY','absolute',4],['LDA','absolute',4],['LDX','absolute',4],['LAX','absolute',4],
                    ['BCS','relative',2],['LDA','postIndexedIndirect',5],['NOP','implied',2],['LAX','postIndexedIndirect',5],['LDY','zeroPageX',4],['LDA','zeroPageX',4],['LDX','zeroPageY',4],['LAX','zeroPageY',4],['CLV','implied',2],['LDA','absoluteY',4],['TSX','implied',2],['NOP','implied',4],['LDY','absoluteX',4],['LDA','absoluteX',4],['LDX','absoluteY',4],['LAX','absoluteY',4],
                    ['CPY','immediate',2],['CMP','preIndexedIndirect',6],['NOP','implied',2],['DCP','preIndexedIndirect',8],['CPY','zeroPage',3],['CMP','zeroPage',3],['DEC','zeroPage',5],['DCP','zeroPage',5],['INY','implied',2],['CMP','immediate',2],['DEX','implied',2],['AXS','immediate',2],['CPY','absolute',4],['CMP','absolute',4],['DEC','absolute',6],['DCP','absolute',6],
                    ['BNE','relative',2],['CMP','postIndexedIndirect',5],['NOP','implied',2],['DCP','postIndexedIndirect',8],['NOP','zeroPageX',4],['CMP','zeroPageX',4],['DEC','zeroPageX',6],['DCP','zeroPageX',6],['CLD','implied',2],['CMP','absoluteY',4],['NOP','implied',2],['DCP','absoluteY',7],['NOP','absoluteX',4],['CMP','absoluteX',4],['DEC','absoluteX',7],['DCP','absoluteX',7],
                    ['CPX','immediate',2],['SBC','preIndexedIndirect',6],['NOP','implied',3],['ISB','preIndexedIndirect',8],['CPX','zeroPage',3],['SBC','zeroPage',3],['INC','zeroPage',5],['ISB','zeroPage',5],['INX','implied',2],['SBC','immediate',2],['NOP','implied',2],['SBC','immediate',2],['CPX','absolute',4],['SBC','absolute',4],['INC','absolute',6],['ISB','absolute',6],
                    ['BEQ','relative',2],['SBC','postIndexedIndirect',5],['NOP','implied',2],['ISB','postIndexedIndirect',8],['NOP','zeroPageX',4],['SBC','zeroPageX',4],['INC','zeroPageX',6],['ISB','zeroPageX',6],['SED','implied',2],['SBC','absoluteY',4],['NOP','implied',2],['ISB','absoluteY',7],['NOP','absoluteX',4],['SBC','absoluteX',4],['INC','absoluteX',7],['ISB','absoluteX',7],
                    ]

    def run(self):
        print(hex(self.registers['PC']),end='  ')
        t=time.time()
        opecode = self.fetch()
        print(hex(opecode), end=' ')
        self.t1.append(time.time()-t)
        t=time.time()
        basename, mode, cycle = self.OPECODE_LIST[opecode]
        print(basename,end='  ')
        #print(basename)
        #print(mode)
        self.t2.append(time.time()-t)
        t=time.time()
        opeland = self.fetch_opeland(mode)
        self.t3.append(time.time()-t)
        #print(opeland)
        print(hex(opeland),end='  =  ')
        if mode not in ['immediate', 'implied', 'accumulator','postIndexedIndirect','indirectAbsolute']:
            print(hex(self.read(opeland)),end='    ')
        t=time.time()
        self.exec(basename, opeland, mode)
        self.t4.append(time.time()-t)
        print('A: '+hex(self.registers['A']),end='  ')
        #print('Y: '+hex(self.registers['Y']),end='  ')
        print('X: '+hex(self.registers['X']),end='  ')
        print('P: '+hex(self.get_p_register()))
        #print('SP: '+hex(self.registers['SP']))
        return(cycle)



