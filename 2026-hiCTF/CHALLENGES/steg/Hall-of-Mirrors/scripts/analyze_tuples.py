# Hall-of-Mirrors — hiCTF (script de solve)
import sys
d = open(sys.argv[1], 'rb').read()
assert d[:8] == b'MIRRORS1'
i = 8
n = None; tuples = []
while i < len(d):
    t = d[i]; i += 1
    if t == 0x00: break
    ln = int.from_bytes(d[i:i+2], 'little'); i += 2
    v = d[i:i+ln]; i += ln
    if t == 1: n = int.from_bytes(v, 'big')
    if t == 0x0A:
        a = int.from_bytes(v[0:32], 'big')
        b = int.from_bytes(v[32:64], 'big')
        c = int.from_bytes(v[64:96], 'big')
        tuples.append((a, b, c))
print('n =', hex(n), 'bits', n.bit_length())
print('nb tuples', len(tuples))
# magnitude de chaque composante (bits) sur quelques triplets
for idx in range(5):
    a, b, c = tuples[idx]
    print(f'[{idx}] a={a.bit_length():3}b b={b.bit_length():3}b c={c.bit_length():3}b  a<n:{a<n} b<n:{b<n} c<n:{c<n}')
# stats: min bit-length par colonne
for col in range(3):
    bl = [tuples[k][col].bit_length() for k in range(len(tuples))]
    print(f'col {col}: min={min(bl)} max={max(bl)} moy={sum(bl)/len(bl):.1f}')
