# Cairn (hiCTF, crypto) : rejoue la marche aléatoire dans le graphe d'isogénies
# décrite dans RULES.md, puis dérive la clé AES-GCM et déchiffre le flag.
# Usage : python -I solve.py <challenge.json> [nb_etapes_test]
import sys, json, hashlib, base64, time
import flint
from Crypto.Cipher import AES

d = json.load(open(sys.argv[1]))           # json Python = entiers en précision arbitraire
T = int(sys.argv[2]) if len(sys.argv) > 2 else d["T"]
p = d["p"]
salt = bytes.fromhex(d["salt_hex"])
L = d["L"]

# GF(p^2) = GF(p)[i]/(i^2+1)
ctx = flint.fq_default_ctx(modulus=flint.fmpz_mod_poly_ctx(p)([1, 0, 1]), var="i")
R = flint.fq_default_poly_ctx(ctx)
I = ctx.gen()

def elt(a, b):
    return ctx(a) + ctx(b) * I

def ab(z):
    c = [int(x) for x in z.to_list()] + [0, 0]
    return c[0], c[1]                          # z = a + b*i

def ser(z):
    a, b = ab(z)
    return a.to_bytes(32, "little") + b.to_bytes(32, "little")

# Phi_l rangé par puissance de Y : coefsY[l][y] = liste de (x_exp, coeff mod p)
coefsY = {}
for l in L:
    t = {}
    for xe, ye, c in d["phi"][str(l)]:
        t.setdefault(ye, []).append((xe, c % p))
    coefsY[l] = t

def step_roots(j, l):
    pw = [ctx(1)]
    for _ in range(l + 1):
        pw.append(pw[-1] * j)                   # puissances j^0..j^(l+1)
    co = [ctx(0)] * (l + 2)
    for ye, lst in coefsY[l].items():
        s = ctx(0)
        for xe, c in lst:
            s += pw[xe] * c
        co[ye] = s
    f = R(co)                                   # f(Y) = Phi_l(j, Y)
    # roots() renvoie les racines DISTINCTES = racines de f_sq (partie sans carré)
    rts = [ab(r) for r, _m in f.roots()]
    rts.sort()                                  # ordre lexicographique (a, b)
    return rts

j = elt(*d["j0"])
t0 = time.time()
for i in range(T):
    h = hashlib.sha256(ser(j) + i.to_bytes(8, "big") + salt).digest()
    l = L[h[0] % 4]
    rts = step_roots(j, l)
    # sanity : graphe supersingulier => f se scinde complètement dans GF(p^2)
    assert len(rts) >= 1
    a, b = rts[h[1] % len(rts)]
    j = elt(a, b)
    if i % 65536 == 0:
        print(f"step {i}  l={l} n={len(rts)}  {time.time()-t0:.1f}s", flush=True)

print("j_T =", ab(j))
if T == d["T"]:
    key = hashlib.sha256(ser(j) + b"IsogenyLabyrinth").digest()
    c = AES.new(key, AES.MODE_GCM, nonce=base64.b64decode(d["nonce_b64"]))
    print(c.decrypt_and_verify(base64.b64decode(d["ciphertext_b64"]),
                               base64.b64decode(d["tag_b64"])))
