# Just Give Me The Flag Man — décodage en couches ("shifting through the bases").
#   1) groupes de 2 caractères = octets en hex écrits à l'envers (unité d'abord),
#      lettres hex en Atbash : a<->z, b<->y, c<->x, d<->w, e<->v, f<->u
#   2) chaîne inversée -> Ascii85
#   3) ROT47 -> Base91
#   4) lettres : Beaufort clé 'm'  (clair = (12 - chiffré) mod 26)
# Usage : python3 solve.py chall.txt
import sys, base64

def base91_decode(s):
    """Décodeur basE91 de référence (alphabet standard de Joachim Henke)."""
    A = ('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
         '0123456789!#$%&()*+,./:;<=>?@[]^_`{|}~"')
    tbl = {c: i for i, c in enumerate(A)}
    v, b, n, out = -1, 0, 0, bytearray()
    for c in s:
        if c not in tbl: continue
        if v < 0: v = tbl[c]; continue
        v += tbl[c] * 91
        b |= v << n
        n += 13 if (v & 8191) > 88 else 14
        while n > 7:
            out.append(b & 255); b >>= 8; n -= 8
        v = -1
    if v + 1: out.append((b | v << n) & 255)
    return bytes(out)

rot47 = lambda b: bytes(33 + (c - 33 + 47) % 94 if 33 <= c <= 126 else c for c in b)

def beaufort_m(s):
    out = []
    for c in s:
        if c.isalpha():
            base = 97 if c.islower() else 65
            out.append(chr(base + (12 - (ord(c) - base)) % 26))
        else:
            out.append(c)
    return ''.join(out)

toks = open(sys.argv[1]).read().split()
atbash_hex = str.maketrans('uvwxyz', 'fedcba')
c1 = bytes(int(t.translate(atbash_hex)[::-1], 16) for t in toks)
c2 = base64.a85decode(c1[::-1])
c3 = base91_decode(rot47(c2).decode()).decode()
print('couche 1 (hex inversé, Atbash) :', c1.decode())
print('couche 2 (inversion + Ascii85) :', c2.decode())
print('couche 3 (ROT47 + Base91)      :', c3)
print('flag (Beaufort clé m)          :', beaufort_m(c3))
