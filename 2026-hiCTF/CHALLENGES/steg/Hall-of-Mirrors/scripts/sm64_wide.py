# Balayage large : flux (avant/arrière), écarts SM64, source de bit, masque éventuel.
import sys, numpy as np, itertools
M64 = (1 << 64) - 1
def sm64(state, n):
    out = []
    for _ in range(n):
        state = (state + 0x9E3779B97F4A7C15) & M64
        z = state
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & M64
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & M64
        out.append(z ^ (z >> 31))
    return out
raw = np.fromfile(sys.argv[1], dtype=np.uint8)
pcm = raw[216:].view('<i2').astype(np.int32)
K = int(sys.argv[2], 16)
R = sm64(K, 1024)
Ru = np.array(R, dtype=np.uint64)
pc8 = np.array([bin(i).count('1') & 1 for i in range(65536)], dtype=np.uint8)
masks = {'none': np.zeros(1024, np.uint8),
         'r&1': (Ru & np.uint64(1)).astype(np.uint8),
         'r>>63': (Ru >> np.uint64(63)).astype(np.uint8),
         'pop(r)': np.array([bin(r).count('1') & 1 for r in R], np.uint8)}
streams = {'pcm': pcm, 'L': pcm[0::2], 'R': pcm[1::2], 'bytes': raw[216:].astype(np.int32)}
for k in list(streams): streams[k + '_rev'] = streams[k][::-1]
starts = (0, 176, 22)
best = []
for (sname, s), k, off, st in itertools.product(streams.items(), range(0, 21), (0, 1), starts):
    for part in ('lo', 'hi', 'mid'):
        if part == 'lo': g = (Ru & np.uint64((1 << k) - 1)).astype(np.int64)
        elif part == 'hi': g = (Ru >> np.uint64(64 - k)).astype(np.int64) if k else np.zeros(1024, np.int64)
        else: g = ((Ru >> np.uint64(32)) & np.uint64((1 << k) - 1)).astype(np.int64)
        idx = st + np.cumsum(g + off) - (g[0] + off)   # première position = st
        if idx[-1] >= len(s): continue
        v = s[idx]
        for bname, bits in (('lsb', (v & 1).astype(np.uint8)), ('pop', pc8[v & 0xFFFF])):
            for mname, m in masks.items():
                b = (bits ^ m).reshape(-1, 8)
                for msb in (1, 0):
                    by = np.packbits(b if msb else b[:, ::-1], axis=1).ravel()
                    sc = ((by[:64] >= 32) & (by[:64] < 127)).mean()
                    t = bytes(by[:64])
                    if sc > 0.8 or b'hiCTF' in t or b'PK\x03\x04' in t or b'\x1f\x8b\x08' in t:
                        best.append((sc, sname, part, k, off, st, bname, mname, msb, t))
best.sort(key=lambda x: -x[0])
for x in best[:15]: print(x)
print('total', len(best))
