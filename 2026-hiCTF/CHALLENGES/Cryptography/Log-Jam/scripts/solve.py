# Log Jam — logarithme discret dans un petit groupe (p premier de 71 bits).
#
#   h = g^x mod p   ->  x = log_g(h)   (PARI znlog : index calculus, quelques secondes)
#   puis : clé AES dérivée de x, déchiffrement AES-GCM (le tag valide la clé).
#
# Usage : python solve.py params.json      (nécessite cypari2 / passagemath-pari et pycryptodome)
import sys, json, hashlib
import cypari2
from Crypto.Cipher import AES

P = json.load(open(sys.argv[1]))
p, g, h = (int(P[k], 16) for k in ('p', 'g', 'h'))
nonce, ct, tag = (bytes.fromhex(P[k]) for k in ('nonce', 'ciphertext', 'tag'))

# 1) Logarithme discret avec PARI : znlog(h, Mod(g, p))
pari = cypari2.Pari()
pari.allocatemem(1 << 30, silent=True)        # pile PARI à 1 Go (8 Mo par défaut : trop peu pour znlog)
x = int(pari(f'znlog(Mod({h},{p}), Mod({g},{p}))'))
assert pow(g, x, p) == h
print('x =', x)

# 2) Dérivations de clé candidates : le tag GCM rejette toute clé fausse
def candidates(x):
    nb = (x.bit_length() + 7) // 8
    forms = {
        'x octets': x.to_bytes(nb, 'big'),
        'x 9 octets': x.to_bytes(9, 'big'),
        'x 16 octets': x.to_bytes(16, 'big'),
        'x 32 octets': x.to_bytes(32, 'big'),
        'x texte': str(x).encode(),
        'x hex': format(x, 'x').encode(),
    }
    for name, b in forms.items():
        yield 'sha256(' + name + ')', hashlib.sha256(b).digest()
        yield 'sha256(' + name + ')[:16]', hashlib.sha256(b).digest()[:16]
        yield 'md5(' + name + ')', hashlib.md5(b).digest()
        if len(b) in (16, 32): yield name, b

for name, key in candidates(x):
    try:
        pt = AES.new(key, AES.MODE_GCM, nonce=nonce).decrypt_and_verify(ct, tag)
        print('clé =', name); print(pt.decode()); break
    except ValueError:
        pass
else:
    print('aucune dérivation candidate ne valide le tag')
