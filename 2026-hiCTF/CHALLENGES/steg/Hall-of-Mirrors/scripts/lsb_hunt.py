# Cherche tout texte ASCII long (>=10) ou "hiCTF"/"MIRR" dans différents flux LSB, 8 alignements de bits.
import sys, re, numpy as np
raw = np.fromfile(sys.argv[1], dtype=np.uint8)[216:]
pcm = raw.view('<i2')
streams = {'samples': pcm & 1, 'L': pcm[0::2] & 1, 'R': pcm[1::2] & 1, 'bytes': raw & 1, 'bit1': (pcm >> 1) & 1}
for name, b in streams.items():
    b = b.astype(np.uint8)
    for align in range(8):
        for msb in (1, 0):
            bb = b[align:]; bb = bb[:len(bb)//8*8].reshape(-1, 8)
            by = np.packbits(bb if msb else bb[:, ::-1], axis=1).tobytes()
            for m in re.finditer(rb'[ -~]{10,}|hiCTF|MIRR|mirr', by):
                print(name, align, msb, 'octet', m.start(), '-> pos', align + 8*m.start(), m.group()[:100])
