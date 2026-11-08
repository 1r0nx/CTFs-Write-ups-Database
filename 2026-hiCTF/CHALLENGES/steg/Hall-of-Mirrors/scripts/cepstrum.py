# Cepstre réel moyen par blocs : un écho de délai D produit un pic au "quéfrence" D.
import sys, numpy as np
d = np.memmap(sys.argv[1], dtype='<i2', mode='r', offset=216).reshape(-1, 2); sr = 48000
N = 8192
def cep(x):
    X = np.fft.rfft(x * np.hanning(len(x)))
    return np.fft.irfft(np.log(np.abs(X) + 1e-6))
for ch in (0, 1):
    for t in [0, 300, 600, 900, 1100, 1300, 1500]:
        x = d[t*sr:(t+20)*sr, ch].astype(np.float64)
        nf = len(x)//N
        C = np.mean([cep(x[i*N:(i+1)*N]) for i in range(nf)], 0)[:3000]
        C[:15] = 0
        top = np.argsort(np.abs(C))[-6:][::-1]
        print(ch, t, [(int(i), round(float(C[i]), 4)) for i in top])
