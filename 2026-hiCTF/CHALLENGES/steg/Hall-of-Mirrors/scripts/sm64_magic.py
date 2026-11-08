# Variantes SM64/GAP/PAR élargies ; on cherche des signatures connues dans les 64 premiers octets extraits.
import sys, numpy as np
M64 = (1 << 64) - 1
def sm64(state, n, pre=False):
    out = []
    for _ in range(n):
        state = (state + 0x9E3779B97F4A7C15) & M64
        z = state
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & M64
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & M64
        out.append(z ^ (z >> 31))
    return out
raw = np.fromfile(sys.argv[1], dtype=np.uint8)
pcm = raw[216:].view('<i2')
K = int(sys.argv[2],16)
R = np.array(sm64(K, 1024), dtype=np.uint64)
MAGIC = [b'hiCTF', b'PK\x03\x04', b'\x1f\x8b\x08', b'BZh9', b'MIRR', b'mirr', b'RIFF', b'\x89PNG', b'7z\xbc', b'flag', b'CTF{', b'\xfd7zXZ']
pc = np.array([bin(i).count('1') & 1 for i in range(65536)], dtype=np.uint8)
streams = {'pcm': pcm.astype(np.int32), 'L': pcm[0::2].astype(np.int32), 'R': pcm[1::2].astype(np.int32),
           'bytes_data': raw[216:].astype(np.int32), 'bytes_file': raw.astype(np.int32),
           'LgtR': (pcm[0::2] > pcm[1::2]).astype(np.int32), 'LxR': (pcm[0::2] ^ pcm[1::2]).astype(np.int32)}
gapf = {}
for k in range(0, 21):
    m = 1 << k
    gapf[f'lo%{m}'] = R % np.uint64(m) if m > 1 else R*0
    gapf[f'hi%{m}'] = R >> np.uint64(64-k) if k else R*0
for m in (1000, 4800, 48000): gapf[f'mod{m}'] = R % np.uint64(m)
found = 0
for sname, s in streams.items():
    for gname, g in gapf.items():
        g = g.astype(np.int64)
        for off in (0, 1, 2):
            for first in (0, 1):
                idx = np.cumsum(g + off)
                if not first: idx = np.concatenate([[0], idx[:-1]])
                if idx.max() >= len(s) or idx.max() == 0: continue
                v = s[idx]
                for bname, bits in (('lsb', v & 1), ('pop', pc[v & 0xFFFF]), ('inv', 1 - (v & 1))):
                    for msb in (1, 0):
                        b = bits.astype(np.uint8).reshape(-1, 8)
                        by = np.packbits(b if msb else b[:, ::-1], axis=1).ravel().tobytes()
                        for mg in MAGIC:
                            if mg in by[:64]:
                                print(sname, gname, off, first, bname, msb, by[:80]); found += 1
print('found', found)
