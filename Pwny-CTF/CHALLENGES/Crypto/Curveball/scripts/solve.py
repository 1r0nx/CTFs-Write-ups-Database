#!/usr/bin/env python3
# Curveball (Pwny-CTF, Crypto) - ECDH avec seulement l'abscisse de Q_a
#
# On joue Bob. ECDH : secret partage S = n_B * Q_a (point d'Alice). La transmission
# n'a donne que l'abscisse Q_a_x. Mais sur une courbe y^2 = x^3+ax+b mod p, connaitre
# x donne y a +/- pres (deux racines carrees) : il y a donc DEUX points Q_a possibles
# (-> deux secrets, un seul marche, comme annonce). On calcule S = n_B * Q_a pour
# chaque y, on derive la cle et on dechiffre.
import hashlib, json
from Crypto.Cipher import AES
from sympy import sqrt_mod

cj = json.load(open("client.json"))["ecdhke_client"]
cp = cj["curve_params"]; a, b, p = cp["a"], cp["b"], cp["p"]
Qax = cj["given"]["Q_a_x"]; nB = cj["given"]["n_B"]
iv = bytes.fromhex(cj["iv"]); ct = bytes.fromhex(cj["ciphertext"])

# arithmetique de courbe elliptique (Weierstrass) mod p
def add(P, Q):
    if P is None: return Q
    if Q is None: return P
    x1, y1 = P; x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0: return None
    m = (3*x1*x1 + a) * pow(2*y1, -1, p) % p if P == Q else (y2-y1) * pow(x2-x1, -1, p) % p
    x3 = (m*m - x1 - x2) % p
    return (x3, (m*(x1-x3) - y1) % p)
def mul(k, P):
    R = None
    while k:
        if k & 1: R = add(R, P)
        P = add(P, P); k >>= 1
    return R

def decrypt(ss_str):                       # cle AES = SHA1(str(secret))[:16]
    key = hashlib.sha1(str(ss_str).encode()).digest()[:16]
    return AES.new(key, AES.MODE_CBC, iv).decrypt(ct)

rhs = (Qax**3 + a*Qax + b) % p
for y in sqrt_mod(rhs, p, all_roots=True):     # deux y possibles
    Sx, Sy = mul(nB, (Qax, y))
    # secret = sha256 des coordonnees (la desc dit sha256(S_x))
    for ss in (hashlib.sha256(str(Sx).encode()).hexdigest(),
               hashlib.sha256((str(Sx)+str(Sy)).encode()).hexdigest()):
        pt = decrypt(ss)
        if b"sigpwny" in pt:
            print(pt.split(b"}")[0].decode() + "}")
