#!/usr/bin/env python3
# Are ya wiening son (Pwny-CTF, Crypto) - attaque de Wiener (petit d, enorme e)
#
# Quand l'exposant prive d est petit (d < n^0.25 / 3), l'enorme e correspondant
# rend d/... bien approxime par les CONVERGENTES du developpement en fraction
# continue de e/n. Pour chaque convergente k/d candidate :
#   phi = (e*d - 1)/k ; p,q racines de x^2 - (n-phi+1)x + n ; si entier -> gagne.
from Crypto.Util.number import long_to_bytes
from sympy import integer_nthroot

n = 128767326226749222149083475036428745644970300119649948221458999875083875437890951425341521563257144723890604454394116660647947280848952888364261577977247563311710534992587520235260641461440191289284680171474898975851063725555307646933546668036930585305366262290086707804687107479147497921806772062367570662023
e = 14651858084426690036858435807468708669195728734122393966364166447981246404241491262885086025852487653225787249518859726929896935579764057555372921211470812350806506060658397403158402387096705678825239657487709286647296884212208964227901237933193926173037064689168794354364763241407707710603467199559116029643
c = 0x192911010ebeadd4b1a52df5c068b7083228acbd158088434cb4ecca08e4bb4790645b0c22c6636a6f256823a45c078730d797880908b8b280dc438b3405c19af1f4ac4fb2750639a5e601bb304f7465826612a61ff2a9eef2e2d70983adfb4694eff9f351d553f739890cfcd9f60fe6bfb0489dae0d7f11156bc5ce403be443

def cont_frac(a, b):                 # developpement en fraction continue de a/b
    while b:
        q = a // b
        yield q
        a, b = b, a - q * b

def convergents(cf):                 # convergentes successives (num, den)
    n0, n1, d0, d1 = 0, 1, 1, 0
    for q in cf:
        n0, n1 = n1, q * n1 + n0
        d0, d1 = d1, q * d1 + d0
        yield n0, d0

for k, d in convergents(cont_frac(e, n)):
    if k == 0 or (e * d - 1) % k:
        continue
    phi = (e * d - 1) // k
    b = n - phi + 1                  # p + q
    disc = b * b - 4 * n
    if disc < 0:
        continue
    r, ok = integer_nthroot(disc, 2)
    if ok and (b + r) % 2 == 0:      # p, q entiers -> d est le bon
        print(long_to_bytes(pow(c, d, n)).decode())
        break
