#!/usr/bin/env python3
# Neutron-Collider (Pwny-CTF, Crypto) - collision MD5 a prefixe choisi
#
# Le serveur donne le flag si on fournit deux chaines x != y, commencant TOUTES
# DEUX par b"sigpwny{", avec md5(x) == md5(y). MD5 est cryptographiquement casse :
# on sait generer des collisions a prefixe identique (fastcoll de Marc Stevens).
#
# GENERATION (fait une fois, binaire fastcoll compile avec boost) :
#   printf 'sigpwny{' > prefix.bin
#   ./fastcoll -p prefix.bin -o collision1.bin collision2.bin
# -> deux fichiers de 192 o commencant par "sigpwny{", differents, meme MD5.
# IMPORTANT : regenerer jusqu'a ce qu'AUCUN octet \n (0x0a) ni \r n'apparaisse,
# car input() cote serveur s'arrete au newline (sinon la chaine est tronquee).
#
# Les deux blocs utilises ici sont sauvegardes dans collision1.bin / collision2.bin.
from pwn import *
import hashlib, re, os
context.log_level = "error"

HERE = os.path.dirname(os.path.abspath(__file__))
a = open(os.path.join(HERE, "collision1.bin"), "rb").read()
b = open(os.path.join(HERE, "collision2.bin"), "rb").read()
assert a[:8] == b[:8] == b"sigpwny{" and a != b
assert hashlib.md5(a).hexdigest() == hashlib.md5(b).hexdigest()
assert all(c not in a + b for c in (10, 13))      # pas de newline (input() s'arreterait)

io = remote("chal.sigpwny.com", 1988)
io.sendlineafter(b"string 1 > ", a)
io.sendlineafter(b"string 2 > ", b)
out = io.recvall(timeout=5)
print(re.search(rb"sigpwny\{[^}]*\}", out).group().decode())
