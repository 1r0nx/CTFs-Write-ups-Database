#!/usr/bin/env python3
# Elgamal-Oracle (Pwny-CTF, Crypto) - oracle de dechiffrement ElGamal reutilise la cle DH
#
# On observe un DH : p, g=2, A=g^a, B=g^b. Le secret partage est g^(ab) = B^a mod p.
# Alice expose un oracle de dechiffrement ElGamal qui utilise le MEME `a` :
#   oracle(c1, c2) = c2 * (c1^a)^-1 mod p     (refuse c2 == 1)
# En posant c1 = B, c2 = 2 :  out = 2 * (B^a)^-1 mod p
# => le secret recherche  B^a = 2 * out^-1 mod p.  Un seul appel suffit.
from pwn import *
import re
context.log_level = "error"

io = remote("chal.sigpwny.com", 1986)
rd = lambda pref: int(io.recvuntil(pref) and io.recvline().strip(), 16)
p = rd(b"p = "); A = rd(b"A = "); B = rd(b"B = ")

io.sendlineafter(b"Enter c1:\n", hex(B).encode())    # c1 = B
io.sendlineafter(b"Enter c2:\n", hex(2).encode())    # c2 = 2 (!= 1)
out = int(io.recvline().strip(), 16)                 # out = 2 * (B^a)^-1
shared = (2 * pow(out, -1, p)) % p                   # B^a = g^(ab) = secret partage

io.sendlineafter(b"Guess the shared secret:\n", hex(shared).encode())
res = io.recvall(timeout=4)
print(re.search(rb"sigpwny\{[^}]*\}", res).group().decode())
