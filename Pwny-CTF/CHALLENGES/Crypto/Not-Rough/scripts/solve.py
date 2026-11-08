#!/usr/bin/env python3
# Not Rough (Pwny-CTF, Crypto) - DH a premier LISSE + exposants petits
#
# "Not rough primes = smooth primes" : p est choisi tel que p-1 est le produit de
# petits premiers (lisse) -> log discret facile (Pohlig-Hellman). MAIS ici les
# exposants prives a,b sont aussi PETITS (<= 100000), donc un simple brute force
# du log discret suffit (comme Merkle). Le flag est XORe avec le secret partage.
from Crypto.Util.number import long_to_bytes
from Crypto.Util.strxor import strxor

g = 5
p = 3994732750984757793415909418853202690017264536679901697055887636451112208609085768686095407237694676577311674417690942534847138200127993858682943825930847
A = 122361642787033242869774181210113436332992137548204178232698839831322961972270560698088730843463640096306717069318664406313636281062333861867496998672739
B = 1985003215394034014102058935054026541253063611279449017294025509652416068614229749959364204543290574391817700248652703188634887220573701652245177567747012
ct = b'i+\xa2\xc4\x00n\xcf\xea\x8b\x8b\xd1D\xd7\x85%{\xcb\xdb\xdd,\x1c\x92\x1a\n\x93\x12\x1f\x8d\x9a\xb6\x19\x8e\xaa\r\xc2<\x9fotf\xbb\xeb\x05\xa0\xaa\xfb\xd28E^*\xadG#\x1b\xe6\xd2\x86\xc6\xd6\x16\xa2'

# brute du log discret : trouve a tel que g^a = A mod p (a <= 100000)
cur, a = g, None
for i in range(1, 100001):
    if cur == A:
        a = i
        break
    cur = (cur * g) % p
key = pow(B, a, p)                 # secret partage = B^a mod p
print(strxor(long_to_bytes(key)[:len(ct)], ct).decode())
