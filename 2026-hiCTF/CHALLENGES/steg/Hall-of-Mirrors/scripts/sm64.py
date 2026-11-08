# Test de l'hypothèse "SM64/GAP/PAR" : SplitMix64(K) donne des écarts entre échantillons,
# on lit la parité (LSB) de chaque échantillon visité, puis on cherche du texte.
import sys, numpy as np
M64 = (1 << 64) - 1
def splitmix64(state):
    while True:
        state = (state + 0x9E3779B97F4A7C15) & M64
        z = state
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & M64
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & M64
        yield z ^ (z >> 31)
d = np.memmap(sys.argv[1], dtype='<i2', mode='r', offset=216)
K = int(sys.argv[2], 16) if len(sys.argv) > 2 else 0x9C4F1E7A3B50D682
streams = {'inter': d, 'L': d[0::2], 'R': d[1::2]}
def pack(bits, msb=True):
    b = np.array(bits, dtype=np.uint8)[: len(bits)//8*8].reshape(-1, 8)
    if not msb: b = b[:, ::-1]
    return np.packbits(b, axis=1).ravel().tobytes()
for mod in [2**k for k in range(1, 17)] + [1000, 4800, 48000]:
    for start_first in (0, 1):
        g = splitmix64(K); idx = []; p = 0 if start_first == 0 else -1
        for _ in range(4000):
            p += next(g) % mod + 1 if start_first else 0
            idx.append(max(p, 0))
            if not start_first: p += next(g) % mod + 1
        idx = np.array(idx)
        for name, s in streams.items():
            if idx[-1] >= len(s): continue
            v = np.asarray(s[idx]).astype(np.int32)
            for kind, bits in (('lsb', v & 1), ('pop', np.array([bin(x & 0xFFFF).count('1') & 1 for x in v]))):
                for msb in (True, False):
                    out = pack(bits, msb)
                    if b'hiCTF' in out or b'CTF' in out or sum(32 <= c < 127 for c in out[:40]) > 36:
                        print(mod, start_first, name, kind, msb, out[:120])
