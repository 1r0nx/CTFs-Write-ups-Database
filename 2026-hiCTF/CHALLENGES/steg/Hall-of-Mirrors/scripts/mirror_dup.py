# Cherche des copies "miroir" : segment identique à un autre lu à l'envers, ou de signe inversé, ou L<->R.
import sys, numpy as np
d = np.memmap(sys.argv[1], dtype='<i2', mode='r', offset=216).reshape(-1, 2)
def keys(x):
    x = x.astype(np.int64) & 0xFFFF
    x = x.astype(np.uint64)
    return (x[:-3] << np.uint64(48)) | (x[1:-2] << np.uint64(32)) | (x[2:-1] << np.uint64(16)) | x[3:]
L = np.asarray(d[:, 0]); R = np.asarray(d[:, 1])
tests = {'L vs rev(L)': (L, L[::-1]), 'R vs rev(R)': (R, R[::-1]), 'L vs R': (L, R),
         'L vs rev(R)': (L, R[::-1]), 'L vs -L': (L, -L), 'L vs -R': (L, -R), 'L vs -rev(L)': (L, -L[::-1])}
for name, (a, b) in tests.items():
    ka, kb = keys(a), keys(b)
    common = np.intersect1d(ka, kb)
    print(name, 'clés communes:', len(common))
