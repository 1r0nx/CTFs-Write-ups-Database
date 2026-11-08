# Déchiffre les entrées NVS (XTS-AES-256, clé = eky||tky, tweak = offset de l'entrée dans la partition).
# Les 64 premiers octets de chaque page (header + bitmap) ne sont pas chiffrés.
import struct
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
flash=open('flash_image.bin','rb').read()
NVS_OFF=0x9000; NVS_SIZE=0x6000
kd=open('nvs_keys_dec.bin','rb').read()
eky=kd[0:32]; tky=kd[32:64]; key=eky+tky   # 64 o -> XTS-AES-256
part=bytearray(flash[NVS_OFF:NVS_OFF+NVS_SIZE])
def dec_entry(partrel_off, ct):
    tw=struct.pack('<I',partrel_off)+b'\0'*12
    c=Cipher(algorithms.AES(key),modes.XTS(tw))
    return c.decryptor().update(ct)
out=bytearray(part)
for page in range(0, NVS_SIZE, 4096):
    for p in range(64, 4096, 32):
        off=page+p
        out[off:off+32]=dec_entry(off, bytes(part[off:off+32]))
open('nvs_plain.bin','wb').write(out)
print('NVS déchiffrée -> nvs_plain.bin')
# aperçu page 0
print(out[0:64].hex())
for p in range(64,64+32*8,32):
    e=out[p:p+32]
    print(f'{p:#06x}', e.hex(), e[8:24])
