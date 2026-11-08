# Parse du TLV MIRRORS1 produit par la VM (cf. datasheet section [3])
import sys
d = open(sys.argv[1], 'rb').read()
assert d[:8] == b'MIRRORS1'
i = 8
names = {1:'n',2:'p',3:'a',4:'b',5:'Gx',6:'Gy',7:'Q',8:'L',9:'count',0x0A:'tuple',0x0B:'sealed'}
recs = []
while i < len(d):
    t = d[i]; i += 1
    if t == 0x00:
        print('fin TLV (type 0x00)'); break
    ln = int.from_bytes(d[i:i+2], 'little'); i += 2
    v = d[i:i+ln]; i += ln
    recs.append((t, v))
    label = names.get(t, hex(t))
    if ln <= 64:
        print(f'type {t:#04x} {label:6} len {ln:4} = {v.hex()}')
    else:
        print(f'type {t:#04x} {label:6} len {ln:4} = {v[:16].hex()}...')
