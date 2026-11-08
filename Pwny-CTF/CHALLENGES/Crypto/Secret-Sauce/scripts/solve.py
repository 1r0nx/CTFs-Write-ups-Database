#!/usr/bin/env python3
# Secret-Sauce (Pwny-CTF, Crypto) - AES dont la S-box est AFFINE => chiffre LINEAIRE
#
# La "sauceBox" fournie vaut sauceBox[i] == i ^ 0xCE pour tout i : la S-box n'est
# donc plus la vraie S-box non-lineaire, mais une simple XOR par une constante
# (affine). Or SubBytes est la SEULE etape non-lineaire d'AES ; ShiftRows,
# MixColumns et AddRoundKey sont lineaires/affines sur GF(2). Resultat : tout le
# chiffrement devient AFFINE :  E_k(p) = M(p) ^ b(k)   avec M lineaire FIXE
# (independant de la cle) et b dependant de la cle.
#
# Mode ECB (blocs independants, meme cle). On connait le 1er bloc de plaintext
# ("Secret Sauce:   ") et tous les blocs de ciphertext. Pour deux blocs :
#   c0 ^ ci = M(p0) ^ M(pi) = M(p0 ^ pi)  =>  pi = p0 ^ M^-1(c0 ^ ci)
# Pas besoin de la cle ! On recupere M = enc(x)^enc(0) (cle quelconque), on
# l'inverse sur GF(2), et on reconstruit chaque bloc de flag.
import aes  # le aes.py du challenge (meme dossier)

sauceBox = [i ^ 0xCE for i in range(256)]   # S-box affine fournie dans chal.txt
ct = bytes.fromhex(
    "2ba6b55e01606ba1e82a38222fcc83e51dc6d4a8b966d65bf7aefa02c2a079a0"
    "ff86bbae2a9fd3688ded4346bddad3666e91be04b93c1cbd4eb7b0e9d64fbb6d"
    "3ea24002c38bf7684d0e215adf3e287492bda2fec3d14869e715d444df632c6a"
    "34a655ffcf674f84001d94a7d73388c7c63a0180ab124395199ceb5a6af08ec0")
blocks = [ct[i:i+16] for i in range(0, len(ct), 16)]
p0 = b"Secret Sauce:   "                     # 1er bloc de plaintext (connu), 16 o

cipher = aes.AES(b"\x00" * 16, Sbox=sauceBox)  # cle arbitraire : E affine
enc = lambda x: int.from_bytes(cipher.encrypt(x), "big")
e0 = enc(b"\x00" * 16)
cols = [enc((1 << b).to_bytes(16, "big")) ^ e0 for b in range(128)]  # M(e_b)

# base de pivots (elimination de Gauss sur GF(2)) pour inverser M
piv = {}
for j in range(128):
    v, c = cols[j], 1 << j
    while v:
        hb = v.bit_length() - 1
        if hb in piv:
            v ^= piv[hb][0]; c ^= piv[hb][1]
        else:
            piv[hb] = (v, c); break

def Minv(target):
    v, c = target, 0
    while v:
        hb = v.bit_length() - 1
        v ^= piv[hb][0]; c ^= piv[hb][1]
    return c

p0i = int.from_bytes(p0, "big")
c0 = int.from_bytes(blocks[0], "big")
out = b"".join((p0i ^ Minv(int.from_bytes(ci, "big") ^ c0)).to_bytes(16, "big") for ci in blocks)
print(out.rstrip(b"\x00").decode())
