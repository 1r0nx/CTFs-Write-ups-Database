# HNP / LLL sur ECDSA a nonces tronques (secp256k1), puis KDF + stream cipher -> flag.
# cf. archivist_datasheet.txt section [3].
import sys
from fpylll import IntegerMatrix, LLL

data = open(sys.argv[1], 'rb').read()
assert data[:8] == b'MIRRORS1'
i = 8
rec = {}
tuples = []
while i < len(data):
    t = data[i]; i += 1
    if t == 0x00: break
    ln = int.from_bytes(data[i:i+2], 'little'); i += 2
    v = data[i:i+ln]; i += ln
    if t == 0x0A:
        tuples.append(tuple(int.from_bytes(v[k:k+32], 'big') for k in (0, 32, 64)))
    else:
        rec[t] = v

n  = int.from_bytes(rec[1], 'big')
p  = int.from_bytes(rec[2], 'big')
a  = int.from_bytes(rec[3], 'big')
b  = int.from_bytes(rec[4], 'big')
Gx = int.from_bytes(rec[5], 'big'); Gy = int.from_bytes(rec[6], 'big')
Qx = int.from_bytes(rec[7][:32], 'big'); Qy = int.from_bytes(rec[7][32:], 'big')
L  = rec[8][0]
sealed = rec[0x0B]
print(f'L={L}  nb sigs={len(tuples)}  sealed={len(sealed)}o')

# --- secp256k1 (Jacobian-free, affine suffisant pour verifier) ---
def inv(x, m): return pow(x, -1, m)
def padd(P, Q):
    if P is None: return Q
    if Q is None: return P
    x1, y1 = P; x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0: return None
    if P == Q:
        l = (3 * x1 * x1 + a) * inv(2 * y1, p) % p
    else:
        l = (y2 - y1) * inv(x2 - x1, p) % p
    x3 = (l * l - x1 - x2) % p
    y3 = (l * (x1 - x3) - y1) % p
    return (x3, y3)
def pmul(k, P):
    R = None
    while k:
        if k & 1: R = padd(R, P)
        P = padd(P, P); k >>= 1
    return R
G = (Gx, Gy); Q = (Qx, Qy)

B = 1 << (256 - L)   # borne supposee sur le nonce (12 bits de poids fort nuls)

def try_model(order, m):
    # order: permutation disant quelle colonne est (h, r, s)
    hs, rs, ss = order
    ts, as_ = [], []
    for k in range(m):
        tp = tuples[k]
        h, r, s = tp[hs], tp[rs], tp[ss]
        sinv = inv(s, n)
        ts.append(r * sinv % n)
        as_.append(h * sinv % n)
    dim = m + 2
    M = IntegerMatrix(dim, dim)
    for j in range(m):
        M[j, j] = n * n
    for j in range(m):
        M[m, j]   = ts[j] * n
        M[m+1, j] = as_[j] * n
    M[m, m]     = B
    M[m+1, m+1] = n * B
    LLL.reduction(M)
    for row in range(dim):
        tag = M[row, m+1]
        if abs(tag) == n * B:
            dB = M[row, m]
            sign = 1 if tag == n * B else -1
            dval = (sign * dB) // B
            dcand = dval % n
            for cand in (dcand, (-dcand) % n):
                if pmul(cand, G) == Q:
                    return cand
    return None

import itertools
found = None
for order in itertools.permutations(range(3)):
    for m in (48, 40, 32, 24):
        if m > len(tuples): continue
        d = try_model(order, m)
        if d is not None:
            print(f'TROUVE d avec order(h,r,s)={order} m={m}')
            found = d
            break
    if found: break

if found is None:
    print('echec: aucun modele (h,r,s)/MSB ne valide d*G==Q'); sys.exit(1)

d = found
print('d =', hex(d))

# --- KDF(d) ---
M64 = (1 << 64) - 1
def kdf(dpriv):
    st = 0x4D6972726F72734B
    D = dpriv.to_bytes(32, 'big')
    out = b''
    for rnd in range(4):
        for bb in D:
            st = ((st ^ bb) * 0x100000001B3) & M64
            st ^= st >> 29
            st = (st * 0x9E3779B97F4A7C15) & M64
            st ^= st >> 32
        st = (st + rnd * 0xFF51AFD7ED558CCD) & M64
        out += st.to_bytes(8, 'big')
    return out  # 32 octets

key32 = kdf(d)
print('key32 =', key32.hex())

# --- stream cipher (type ChaCha/Threefish mix) ---
def rotl(v, nbits): return ((v << nbits) | (v >> (64 - nbits))) & M64
def keystream_blocks(key32, nblocks):
    a_, b_, c_, dd = [int.from_bytes(key32[k:k+8], 'little') for k in (0, 8, 16, 24)]
    ctr = 0
    for _ in range(nblocks):
        ctr = (ctr + 0x9E3779B97F4A7C15) & M64
        dd ^= ctr
        A, Bx, C, Dx = a_, b_, c_, dd
        for _ in range(4):
            A = (A + Bx) & M64; Dx = rotl(Dx ^ A, 32)
            C = (C + Dx) & M64; Bx = rotl(Bx ^ C, 24)
            A = (A + Bx) & M64; Dx = rotl(Dx ^ A, 16)
            C = (C + Dx) & M64; Bx = rotl(Bx ^ C, 37)
        yield ((A ^ C) & M64).to_bytes(8, 'little')
        a_, b_, c_, dd = A, Bx, C, Dx  # etat chaine

nb = (len(sealed) + 7) // 8
ks = b''.join(keystream_blocks(key32, nb))[:len(sealed)]
plain = bytes(x ^ y for x, y in zip(sealed, ks))
print('dechiffre (hex):', plain.hex())
print('dechiffre (repr):', repr(plain))
