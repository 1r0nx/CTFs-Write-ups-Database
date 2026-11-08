# Démodulation du texte caché dans le spectrogramme de hall-of-mirrors.wav.
# Chaque "pixel" du texte est un ton pur ; les lignes de pixels sont espacées de ~193.6 Hz.
# On mesure l'énergie exactement à ces fréquences (bins FFT étroits) -> image quasi sans bruit.
# Usage : python3 -I demod.py fichier.wav t0 t1 sortie.png
import sys, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
w, a, b, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
sr = 48000
d = np.memmap(w, dtype='<i2', mode='r', offset=216).reshape(-1, 2)
x = d[int(a*sr):int(b*sr)].astype(np.float32).sum(1)          # L+R (le texte est sur les 2 canaux)
rows = [10877 + 194.0*k for k in range(14)][::-1] + [6800 + 194.0*k for k in range(14)][::-1]  # haut -> bas (pics mesurés)
N, hop = 4800, 1200                                            # fenêtre 0.1 s, pas 25 ms
nf = (len(x) - N) // hop
idx = np.arange(N)[None, :] + hop*np.arange(nf)[:, None]
X = np.abs(np.fft.rfft(x[idx]*np.hanning(N), axis=1))**2
img = np.array([X[:, int(round(f*N/sr))-1:int(round(f*N/sr))+2].sum(1) for f in rows])
img = np.log10(img); img -= np.median(img, 1, keepdims=True)
plt.figure(figsize=(int((b-a)*1.2)+4, 5)); plt.imshow(img, aspect='auto', cmap='gray', vmin=0, vmax=1.5, extent=[a, b, 28, 0])
plt.xticks(np.arange(int(a), int(b)+1, 1)); plt.tight_layout(); plt.savefig(out, dpi=50)
