#!/usr/bin/env python3
# Add-One (Pwny-CTF, Crypto) - manipulation d'IV en AES-CBC (1 bloc)
#
# Le serveur chiffre un entier aleatoire P (1 bloc de 16 o) : C = E_k(P ^ IV).
# On doit fournir (iv', C') tels que decrypt(C', iv') == P + 1.
# En CBC un bloc : decrypt(C, iv) = D_k(C) ^ iv. Avec l'IV d'origine on a
#   D_k(C) ^ IV = P. En REUTILISANT C et en changeant juste l'IV :
#   decrypt(C, iv') = D_k(C) ^ iv' = P ^ (IV ^ iv').
# En posant iv' = IV ^ 1 (flip du bit de poids faible), on obtient P ^ 1, qui vaut
# P + 1 SEULEMENT si P est pair (pas de retenue). P aleatoire -> ~50% de reussite,
# donc on reconnecte jusqu'a tomber sur un P pair. (Le flag le confirme :).)
from pwn import *
import re
context.log_level = "error"

for _ in range(50):
    io = remote("chal.sigpwny.com", 1987)
    io.recvuntil(b"iv = "); iv = bytes.fromhex(io.recvline().strip().decode())
    io.recvuntil(b"original_number = "); C = bytes.fromhex(io.recvline().strip().decode())
    ivp = bytearray(iv); ivp[-1] ^= 1                 # iv' = IV ^ 1
    io.sendlineafter(b"iv = ", bytes(ivp).hex().encode())
    io.sendlineafter(b"+ 1) = ", C.hex().encode())    # on renvoie le MEME C
    out = io.recvall(timeout=4); io.close()
    m = re.search(rb"sigpwny\{[^}]*\}", out)
    if m:
        print(m.group().decode()); break
