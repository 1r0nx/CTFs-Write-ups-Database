#!/usr/bin/env python3
"""0byte (battleCTF) - reconstruit le flag depuis le contenu du C2 (drop.ini).
Usage: python3 solve.py           (lit work/drop.b64 = blob base64 recupere au C2)
"""
import base64, gzip, pickle, pickletools, io, os

here = os.path.dirname(__file__)
b64 = open(os.path.join(here, "drop.b64"), "rb").read()

raw  = base64.b64decode(b64)
blob = gzip.decompress(raw)                      # pickle protocole 4
pickletools.dis(blob, io.StringIO())             # verif: BINBYTES seulement (safe)
payload = bytes.fromhex(pickle.loads(blob).decode())

ns  = lambda b: bytes(((x << 4) | (x >> 4)) & 0xFF for x in b)
elf = ns(payload)[::-1]                           # -> ELF64
assert elf[:4] == b"\x7fELF"

# rejoue la VM BMI2 de .text sur mask/message de .data
mem = bytearray(0x40)
mem[0:8]       = bytes([0xBA, 0xBA, 0xBA, 0xB0, 0, 0, 0, 0])   # mask
mem[8:8 + 15]  = b"Here We Go...!\n"                            # message (leurre)
rd = lambda a: int.from_bytes(mem[a - 0x402000:a - 0x402000 + 8], "little")
wr = lambda a, v: mem.__setitem__(a - 0x402000, v & 0xFF)

def pext(src, mask):
    r = k = 0
    for i in range(64):
        if (mask >> i) & 1:
            if (src >> i) & 1: r |= 1 << k
            k += 1
    return r

def pdep(src, mask):
    r = k = 0
    for i in range(64):
        if (mask >> i) & 1:
            if (src >> k) & 1: r |= 1 << i
            k += 1
    return r

rax = rd(0x402000)
for c, a in [(0x890,0x40201f),(0x80a,0x40201e),(0xa12,0x40201d),(0xa30,0x40201c),
             (0xa90,0x40201b),(0xa90,0x40201a),(0xa02,0x402019),(0xa08,0x402018)]: wr(a, pext(c, rax))
for c, a in [(0xa88,0x402028),(0xa22,0x402027),(0xa02,0x402026),(0xa80,0x402025),
             (0xa8a,0x402024),(0xa12,0x402023),(0x810,0x402022),(0xaaa,0x402021)]: wr(a, pext(c, rax))
wr(0x402020, rd(0x40201f) ^ 0x12)
wr(0x40202f, 0x3b ^ rd(0x402020))
wr(0x40202e, pext(0xaa2, rax)); wr(0x40202d, pext(0xa1a, rax))
wr(0x40202c, rd(0x402028))
wr(0x40202b, (pdep((rd(0x402027) + 5) & 0xFFFFFFFFFFFFFFFF, 0x62) + 5) & 0xFF)
wr(0x40202a, 0x6e)
wr(0x402029, bin(0x1337).count("1") + 0x3d)
print(bytes(mem[0x18:0x30]).decode())            # battleCTF{DespairEnergy}
