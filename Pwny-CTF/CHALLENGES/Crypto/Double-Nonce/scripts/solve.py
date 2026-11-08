#!/usr/bin/env python3
# Double-Nonce (Pwny-CTF, Crypto) - reutilisation du nonce k en ECDSA (secp256k1)
#
# ECDSA : pour un message de hash z, nonce k, cle privee d :
#   r = (k*G).x mod n ,  s = k^-1 (z + d*r) mod n
# Le nonce k DOIT etre unique. Ici deux signatures (msg1, msg2) reutilisent le
# MEME k (on le voit : r1 == r2). Alors :
#   s1 - s2 = k^-1 (z1 - z2)  =>  k = (z1 - z2) / (s1 - s2) mod n
#   s1 = k^-1 (z1 + d*r)      =>  d = (s1*k - z1) / r mod n
# La cle privee d est ensuite utilisee comme cle AES pour chiffrer le flag.
import hashlib, json
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141  # ordre secp256k1
o = json.load(open("out.txt"))
z1 = int.from_bytes(hashlib.sha256(o["msg1"].encode()).digest(), "big")
z2 = int.from_bytes(hashlib.sha256(o["msg2"].encode()).digest(), "big")
r1, s1 = (int(x, 16) for x in o["sig1"])
r2, s2 = (int(x, 16) for x in o["sig2"])
assert r1 == r2                                   # meme nonce -> meme r

k = ((z1 - z2) * pow(s1 - s2, -1, n)) % n
d = ((s1 * k - z1) * pow(r1, -1, n)) % n

pt = AES.new(int(d).to_bytes(32, "big"), AES.MODE_CBC,
             bytes.fromhex(o["iv"])).decrypt(bytes.fromhex(o["encrypted_flag"]))
print(unpad(pt, 16).decode())
