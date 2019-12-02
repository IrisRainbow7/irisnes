class Cassette:
    def __init__(self, cassette_path):
        with open(cassette_path, 'rb') as f:
            self.cassette_data = f.read()
        if [hex(i) for i in self.cassette_data[:4]] != ['0x4e', '0x45', '0x53', '0x1a']:
            raise RuntimeError('File is NOT iNES format')
        character_rom_start = 0x10 + self.cassette_data[4] * 0x4000
        character_rom_end = character_rom_start + self.cassette_data[5] * 0x2000
        self.program_rom = self.cassette_data[0x10:character_rom_start - 1]
        self.character_rom = self.cassette_data[character_rom_start:character_rom_end - 1]

    def sprite(self, n):
        sprite_data = self.character_rom[n * 0x10:(n+1) * 0x10]
        la = []
        lb = []
        for i in range(8):
            la.append(sprite_data[i])
            lb.append(sprite_data[i+8])
        for i in range(len(la)):
            la[i] = list(bin(la[i])[2:].zfill(8))
            lb[i] = list(bin(lb[i])[2:].zfill(8))
            la[i] = list(map(int,la[i]))
            lb[i] = list(map(int,lb[i]))
        sprite_image_data = []
        for i in range(len(la)):
            sprite_image_data.append(list(map(sum,zip(la[i],lb[i]))))
        return(sprite_image_data)
