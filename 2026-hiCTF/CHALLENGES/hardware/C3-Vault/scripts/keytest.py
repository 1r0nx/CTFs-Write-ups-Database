# C3-Vault — hiCTF (script de solve)
import struct
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
flash = open('flash_image.bin','rb').read()
k0 = bytes.fromhex('a60e11f7e712272a9cdf3d656ad89282e861dc0ffd2fc127f7f74da513654d7f')
def wordrev(b):  # inverse l'ordre des octets dans chaque mot de 32 bits
    return b''.join(b[i:i+4][::-1] for i in range(0,len(b),4))
variants = {
    'asis': k0,
    'reversed': k0[::-1],
    'wordrev': wordrev(k0),
    'wordrev_then_rev': wordrev(k0)[::-1],
    'swap_halves': k0[16:]+k0[:16],
    'rev_halves': k0[:16][::-1]+k0[16:][::-1],
}
def xts_dec(key, addr, indata):
    pad_left = addr % 0x80
    buf=(b'\0'*pad_left)+indata
    pr=len(buf)%0x80
    if pr: buf+=b'\0'*(0x80-pr)
    out=b''; a=addr-pad_left
    for off in range(0,len(buf),0x80):
        blk=buf[off:off+0x80]
        tw=struct.pack('<I',a&~0x7F)+b'\0'*12; a+=0x80
        c=Cipher(algorithms.AES(key),modes.XTS(tw))
        out+=c.decryptor().update(blk[::-1])[::-1]
    if pad_left: out=out[pad_left:]
    if pr: out=out[:len(out)-(0x80-pr)]
    return out
seg = flash[0x8000:0x9000]
for name,k in variants.items():
    d = xts_dec(k, 0x8000, seg)
    magic = d[:2].hex()
    hit = d[:2]==b'\xaa\x50'
    print(f'{name:18} first2={magic} {"<-- MAGIC OK" if hit else ""} {d[:16].hex()}')
