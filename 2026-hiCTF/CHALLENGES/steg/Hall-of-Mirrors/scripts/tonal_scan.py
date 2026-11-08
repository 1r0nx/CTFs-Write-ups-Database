# Cherche des tons stables (lignes horizontales du spectrogramme) dans M=L+R et S=L-R, par blocs de 30 s.
import sys, numpy as np
from scipy.ndimage import median_filter
d = np.memmap(sys.argv[1], dtype='<i2', mode='r', offset=216).reshape(-1, 2); sr = 48000; N = 8192
for blk in range(0, 1560, 30):
    s = d[blk*sr:(blk+30)*sr].astype(np.float32)
    for name, x in (('M', s[:, 0] + s[:, 1]), ('S', s[:, 0] - s[:, 1])):
        nf = len(x)//N
        P = (np.abs(np.fft.rfft(x[:nf*N].reshape(nf, N)*np.hanning(N), axis=1))**2).mean(0)
        r = P / median_filter(P, 41)
        f = np.arange(len(r))*sr/N
        hit = np.nonzero((r > 4) & (f > 1000))[0]
        if len(hit): print(blk, name, len(hit), [int(f[i]) for i in hit[:12]])
