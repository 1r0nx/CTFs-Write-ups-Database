# Hypothèse "parity coding" : régions consécutives de longueur gap_i (SM64), bit_i = XOR des LSB de la région.
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
R = sm64(int(sys.argv[2], 16), 512)
Rhi = np.array([r >> 32 for r in R], np.int64); Rlo = np.array([r & 0xFFFFFFFF for r in R], np.int64)
streams = {'pcm': pcm & 1, 'L': pcm[0::2] & 1, 'R': pcm[1::2] & 1, 'bytes': raw & 1}
cs = {k: np.concatenate([[0], np.cumsum(v.astype(np.int64))]) for k, v in streams.items()}   # somme cumulée des LSB
Gs = list(range(2, 70000))
for G in Gs:
    g = ((Rhi % G) * ((1 << 32) % G) + Rlo % G) % G
    for off in (0, 1):
        ends = np.cumsum(g + off); starts = ends - (g + off)
        for sn, c in cs.items():
            if ends[-1] >= len(c): continue
            b = ((c[ends] - c[starts]) & 1).astype(np.uint8)
            for msb in (1, 0):
                bb = b.reshape(-1, 8)
                by = np.packbits(bb if msb else bb[:, ::-1], axis=1).ravel()
                sc = ((by >= 32) & (by < 127)).mean()
                if sc > 0.8 or b'hiCTF' in bytes(by):
                    print(G, off, sn, msb, round(sc, 2), bytes(by[:64]), flush=True)
