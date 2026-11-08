#!/usr/bin/env python3
# Pad-Thai (Pwny-CTF, Crypto) - RSA e=3 avec padding FIXE connu -> Coppersmith
#
# Chiffrement : msg = b'\x01'*(512 - len(flag)) + flag ; ct = msg^3 mod N (e=3).
# Le padding est CONSTANT et connu (que des 0x01). En notant L = len(flag) :
#   m = A + x   avec A = int(b'\x01'*(512-L)) * 256^L  (connu)  et  x = int(flag) < 256^L.
# On cherche donc une PETITE racine x de  f(x) = (A + x)^3 - ct ≡ 0 (mod N).
# Coppersmith / Howgrave-Graham : faisable tant que x < N^(1/e) = N^(1/3)
# (N ~4096 bits -> ~170 octets ; le flag est bien plus court). Un reseau de
# dimension 4 (m=1) suffit ici. On brute la longueur L (inconnue).
#
# NB : LLL entier (pur Python) dans coppersmith.py. Le flag sort a L=32
# (quelques minutes de brute sur L=8..32).
import sys
from Crypto.Util.number import long_to_bytes
import coppersmith as cop

exec(open("output.txt").read().replace("N =", "N=").replace("ct =", "ct="))

for L in range(8, 86):
    A = int.from_bytes(b'\x01' * (512 - L), 'big') * (256 ** L)
    X = 256 ** L
    fc = [(pow(A, 3) - ct) % N, (3 * A * A) % N, (3 * A) % N, 1]   # (A+x)^3 - ct
    g = cop.small_roots(fc, N, X, m=1, t=1)
    for r in cop.roots_of(g, X):
        if r > 0 and pow(A + r, 3, N) == ct:
            print(f"L={L}: {long_to_bytes(r).decode()}")
            sys.exit()
