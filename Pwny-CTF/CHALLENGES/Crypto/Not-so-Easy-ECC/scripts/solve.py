#!/usr/bin/env python3
# Not-so-Easy-ECC (Pwny-CTF, Crypto) - on CHOISIT la courbe -> courbe singuliere
#
# Le serveur nous laisse choisir p, a, b de  y^2 = x^3 + a*x + b (mod p), tire un
# point P et un k, et demande k a partir de P et k*P (ECDLP). On rend l'ECDLP
# TRIVIAL en choisissant une courbe SINGULIERE : a = b = 0 -> y^2 = x^3 (cusp).
# Le groupe des points non-singuliers est alors isomorphe au groupe ADDITIF
# (F_p, +) via la carte  t = x / y . Donc k*P  <->  k * t_P , d'ou :
#     k = t_{kP} * t_P^-1 mod p
from pwn import *
from Crypto.Util.number import getPrime
import re
context.log_level = "error"

io = remote("chal.sigpwny.com", 1990)
p = getPrime(128)
io.sendlineafter(b"the prime p (128 bits): ", str(p).encode())
io.sendlineafter(b"coefficient a: ", b"0")       # a = 0
io.sendlineafter(b"coefficient b: ", b"0")       # b = 0  -> courbe singuliere (cusp)

def getpt(pref):
    io.recvuntil(pref)
    x, y = map(int, re.search(r"\((\d+),(\d+)\)", io.recvline().decode()).groups())
    return x, y

Px, Py = getpt(b"point P on the curve: ")
Qx, Qy = getpt(b"here's k*P: ")
tP = (Px * pow(Py, -1, p)) % p                   # t = x/y (carte vers (F_p,+))
tQ = (Qx * pow(Qy, -1, p)) % p
k = (tQ * pow(tP, -1, p)) % p                    # k = t_{kP} / t_P mod p

io.sendlineafter(b"What is k? ", str(k).encode())
out = io.recvall(timeout=4)
print(re.search(rb"sigpwny\{[^}]*\}", out).group().decode())
