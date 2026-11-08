# Balayage de variantes SM64/GAP/PAR ; score = part d'octets ASCII (<0x80) dans les 300 premiers octets.
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
d = np.memmap(sys.argv[1], dtype='<i2', mode='r', offset=216).reshape(-1, 2)
K = 0x9C4F1E7A3B50D682
R = sm64(K, 2400)
flat = d.reshape(-1)
pc = np.array([bin(i).count('1') & 1 for i in range(65536)], dtype=np.uint8)
def bitsrcs(idx, frame):
    if frame:
        f = np.asarray(d[idx]).astype(np.int32)
        return {'L': f[:, 0] & 1, 'R': f[:, 1] & 1, 'LxR': (f[:, 0] ^ f[:, 1]) & 1, 'L+R': (f[:, 0] + f[:, 1]) & 1,
                'popLR': pc[(f[:, 0] & 0xFFFF)] ^ pc[(f[:, 1] & 0xFFFF)]}
    v = np.asarray(flat[idx]).astype(np.int32)
    return {'s': v & 1, 'pop': pc[v & 0xFFFF], 'sign': (v < 0).astype(int)}
res = []
for frame in (0, 1):
    n = len(d) if frame else len(flat)
    gaps = {}
    for m in [2**k for k in range(1, 21)] + [1000, 4800, 48000, 96000]:
        for off in (0, 1):
            gaps[f'%{m}+{off}'] = [r % m + off for r in R]
            gaps[f'>>{64-m.bit_length()+1}%{m}+{off}'] = [(r >> 32) % m + off for r in R]
    gaps['absolute%n'] = None
    for gname, g in gaps.items():
        idx = np.array([r % n for r in R]) if g is None else np.cumsum(g)
        if idx.max() >= n: continue
        for sname, bits in bitsrcs(idx, frame).items():
            b = np.asarray(bits, np.uint8)[:2400]
            for msb in (1, 0):
                bb = b.reshape(-1, 8) if msb else b.reshape(-1, 8)[:, ::-1]
                by = np.packbits(bb, axis=1).ravel()
                res.append(((by < 0x80).mean(), frame, gname, sname, msb, bytes(by[:60])))
res.sort(key=lambda t: -t[0])
for r in res[:12]: print(r)
