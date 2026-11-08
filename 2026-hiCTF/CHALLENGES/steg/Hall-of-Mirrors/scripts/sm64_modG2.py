# gap = r % G + off, G de 2 à Gmax ; bit = LSB ; score ASCII imprimable sur 32 octets.
import sys, numpy as np
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
raw = np.fromfile(sys.argv[1], dtype=np.uint8)[216:]
pcm = raw.view('<i2')
R = sm64(int(sys.argv[2], 16), 160)
streams = {'pcm': (pcm & 1).astype(np.uint8), 'L': (pcm[0::2] & 1).astype(np.uint8),
           'R': (pcm[1::2] & 1).astype(np.uint8), 'bytes': (raw & 1).astype(np.uint8)}
Rhi = np.array([r >> 32 for r in R], dtype=np.int64); Rlo = np.array([r & 0xFFFFFFFF for r in R], dtype=np.int64)
for G in range(int(sys.argv[4]), int(sys.argv[3])):
    # r % G exact sur 64 bits : (hi*2^32 + lo) % G
    g = ((Rhi % G) * ((1 << 32) % G) + Rlo % G) % G
    for off in (0, 1):
        c = np.cumsum(g + off)
        for first in (0, 1):
            idx = c if first else c - c[0]
            for sn, s in streams.items():
                if idx[-1] >= len(s): continue
                b = s[idx]
                for msb in (1, 0):
                    bb = b.reshape(-1, 8)
                    by = np.packbits(bb if msb else bb[:, ::-1], axis=1).ravel()
                    sc = ((by >= 32) & (by < 127)).mean()
                    if sc > 0.8:
                        print(G, off, first, sn, msb, round(sc, 2), bytes(by), flush=True)
