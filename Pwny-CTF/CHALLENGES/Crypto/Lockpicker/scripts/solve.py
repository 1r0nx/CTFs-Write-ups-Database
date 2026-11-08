#!/usr/bin/env python3
# Lockpicker (Pwny-CTF, Crypto) - factorisation par GCD de modules RSA partages
#
# 1000 cles publiques RSA ; le flag est chiffre (PKCS1_OAEP) avec l'une d'elles ;
# on n'a aucune cle privee. Faille : si deux modules partagent un facteur premier
# (mauvaise entropie du generateur -> premiers reutilises), alors gcd(n_i, n_j) = p
# revele ce facteur commun. On factorise n = p*q, on reconstruit la cle privee, et
# on dechiffre le flag.
import glob, math, base64, tarfile, tempfile, os
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Util.number import inverse

HERE = os.path.dirname(os.path.abspath(__file__))
tmp = tempfile.mkdtemp()
with tarfile.open(os.path.join(HERE, "keys.tar.xz")) as t:
    t.extractall(tmp)

keys = [(f, RSA.import_key(open(f).read())) for f in glob.glob(tmp + "/keys/*.pem")]
ns = [k.n for _, k in keys]

# GCD par paires : trouver deux modules a facteur commun
shared = i = j = None
for a in range(len(ns)):
    for b in range(a + 1, len(ns)):
        g = math.gcd(ns[a], ns[b])
        if g > 1:
            shared, i, j = g, a, b
            break
    if shared:
        break

flag_ct = base64.b64decode(open(os.path.join(HERE, "flag_enc")).read())
for idx in (i, j):                        # l'une des deux a chiffre le flag
    f, k = keys[idx]
    p = shared; q = k.n // p
    d = inverse(k.e, (p - 1) * (q - 1))
    priv = RSA.construct((k.n, k.e, d, p, q))
    try:
        print(PKCS1_OAEP.new(priv).decrypt(flag_ct).decode())
        break
    except ValueError:
        pass
