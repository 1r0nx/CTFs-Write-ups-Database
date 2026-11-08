#!/usr/bin/env python3
# Technically RSA (Pwny-CTF, Crypto) - "any prime should be safe, right?"
#
# n est PAIR (finit par 2) -> l'un des facteurs est p=2 (qui est bien un nombre
# premier... "technically"). Donc n = 2 * q, q = n//2 premier.
# phi(n) = (2-1)*(q-1) = q-1 ; d = e^-1 mod phi ; m = c^d mod n.
from sympy import isprime
from Crypto.Util.number import long_to_bytes, inverse

c = 82879607708421968292546182472929723369055465359424003647490025059797153627599
e = 3
n = 159363030450659905883191818341959600271746776156721659104530831624765969501522

assert n % 2 == 0          # n pair -> p = 2
q = n // 2
assert isprime(q)
phi = (2 - 1) * (q - 1)
d = inverse(e, phi)
print(long_to_bytes(pow(c, d, n)).decode())
