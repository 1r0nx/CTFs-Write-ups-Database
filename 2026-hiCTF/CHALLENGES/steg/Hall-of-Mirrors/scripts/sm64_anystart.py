# Départ inconnu : pour des écarts SM64 fixés (offsets relatifs c_i), cherche tout s tel que
# lsb[s + c_i] == bits("hiCTF{") pour i = 0..47  (filtrage progressif des candidats).
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
R = sm64(int(sys.argv[2], 16), 48)
streams = {'pcm': (pcm & 1).astype(np.uint8), 'L': (pcm[0::2] & 1).astype(np.uint8), 'R': (pcm[1::2] & 1).astype(np.uint8)}
for tgt in (b'hiCTF{',):
    for msb in (1, 0):
        t = np.unpackbits(np.frombuffer(tgt, np.uint8)) if msb else np.unpackbits(np.frombuffer(tgt, np.uint8), bitorder='little')
        for mode in ['lo', 'hi']:
            for k in range(1, 21):
                g = [(r & ((1 << k) - 1)) if mode == 'lo' else (r >> (64 - k)) for r in R]
                for off in (0, 1):
                    c = np.cumsum(np.array(g, np.int64) + off); c -= c[0]
                    for sn, s in streams.items():
                        n = len(s) - c[-1]
                        cand = np.nonzero(s[c[0]:c[0] + n] == t[0])[0]
                        for i in range(1, 48):
                            cand = cand[s[cand + c[i]] == t[i]]
                            if len(cand) == 0: break
                        if len(cand):
                            print('TROUVÉ', tgt, msb, mode, k, off, sn, cand[:5], flush=True)
print('fin')
