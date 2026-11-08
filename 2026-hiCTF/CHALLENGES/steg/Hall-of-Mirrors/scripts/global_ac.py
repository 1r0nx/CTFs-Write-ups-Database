# Autocorrélation globale (tous décalages) d'un canal blanchi : pics = segments recopiés ailleurs (échos lointains).
import sys, numpy as np, scipy.fft as F
d = np.memmap(sys.argv[1], dtype='<i2', mode='r', offset=216).reshape(-1, 2)
ch = int(sys.argv[2])
x = np.asarray(d[:, ch], dtype=np.float32)
n = 1 << 28
X = F.rfft(x, n, workers=8); del x
mag = np.abs(X); 
from scipy.ndimage import uniform_filter1d
X /= (uniform_filter1d(mag, 4001) + 1e-3)       # blanchiment spectral doux
del mag
P = (X.real**2 + X.imag**2).astype(np.float32); del X
r = F.irfft(P, n, workers=8)[: len(d)]; del P
r /= r[0]
r[:200] = 0
top = np.argpartition(np.abs(r), -25)[-25:]
top = top[np.argsort(-np.abs(r[top]))]
print('bruit typique', float(np.std(r[1000:2000000])))
for i in top: print(int(i), round(i/48000, 3), 's', round(float(r[i]), 5))
