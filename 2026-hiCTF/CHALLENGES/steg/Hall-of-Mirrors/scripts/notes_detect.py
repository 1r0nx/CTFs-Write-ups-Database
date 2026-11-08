# Détecte les notes graves (150-1000 Hz) : instant, fréquence, durée, canal.
import sys, numpy as np
d = np.memmap(sys.argv[1], dtype='<i2', mode='r', offset=216).reshape(-1, 2); sr = 48000
N, hop = 4800, 960                       # fenêtre 0.1 s (résolution 10 Hz), pas 20 ms
f = np.fft.rfftfreq(N, 1/sr); band = (f >= 150) & (f <= 1000)
out = []
for ch in (0, 1):
    for blk in range(0, 1560, 60):
        x = d[blk*sr:(blk+60)*sr + N, ch].astype(np.float32)
        nf = (len(x) - N)//hop
        idx = np.arange(N)[None, :] + hop*np.arange(nf)[:, None]
        S = np.abs(np.fft.rfft(x[idx]*np.hanning(N), axis=1))[:, band]**2
        S /= np.median(S, 0, keepdims=True)
        pk = S.max(1); fi = S.argmax(1)
        on = pk > 30
        i = 0
        while i < nf:
            if on[i]:
                j = i
                while j < nf and on[j]: j += 1
                k = i + np.argmax(pk[i:j])
                out.append((ch, round(blk + (i*hop + N/2)/sr, 3), round(float(f[band][fi[k]]), 1), round((j-i)*hop/sr, 2), round(float(pk[k]))))
                i = j
            else: i += 1
np.save('notes.npy', np.array(out))
print(len(out)); [print(o) for o in out[:60]]
