#!/usr/bin/env python3
# Diagonal (Pwny-CTF, Crypto) - fuite du secret via M^d d'une matrice CHOISIE
#
# Le serveur tire un secret d (~1e9..1e10), nous laisse CHOISIR une matrice 3x3 M,
# calcule M^d, et renvoie  res = M[0,0]+M[1,1]+M[2,2] + M[0,1]+M[1,2]+M[0,2].
# On choisit une matrice triangulaire unipotente :
#     M = [[1,1,0],
#          [0,1,0],
#          [0,0,1]]
# alors M^d = [[1,d,0],[0,1,0],[0,0,1]]  (M^d met d en position [0,1]).
# => res = 1+1+1 + d + 0 + 0 = d + 3  =>  secret = res - 3.
from pwn import *
import re
context.log_level = "error"

io = remote("chal.sigpwny.com", 1989)
io.recvuntil(b"Welcome")
for v in (1, 1, 0,  0, 1, 0,  0, 0, 1):          # M choisie
    io.sendlineafter(b"= ", str(v).encode())
io.recvuntil(b"Have fun: ")
res = int(io.recvline().strip())
io.sendlineafter(b"Make a guess: ", str(res - 3).encode())   # secret = res - 3
out = io.recvall(timeout=4)
print(re.search(rb"sigpwny\{[^}]*\}", out).group().decode())
