# Déchiffrement Flash Encryption ESP32-C3 (XTS-AES-128). Clé = BLOCK_KEY0 INVERSÉE (32 o).
import struct
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
KEY = bytes.fromhex('a60e11f7e712272a9cdf3d656ad89282e861dc0ffd2fc127f7f74da513654d7f')[::-1]
def xts_decrypt(key, addr, indata):
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
if __name__=='__main__':
    import sys
    flash=open('flash_image.bin','rb').read()
    a=int(sys.argv[1],0); n=int(sys.argv[2],0)
    open(sys.argv[3],'wb').write(xts_decrypt(KEY,a,flash[a:a+n]))
    print(f'déchiffré {n:#x} @ {a:#x} -> {sys.argv[3]}')
