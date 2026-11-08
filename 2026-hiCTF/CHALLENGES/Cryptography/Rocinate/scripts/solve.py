# Rocinate — le générateur `random` de Python (Mersenne Twister) n'est pas cryptographique.
#
# chall.py tire avec random.randint(1, N) : r, e, a, b, puis les 100 c_i (publiés).
#  -> on reconstruit l'état de MT19937 à partir des c_i, on remonte le temps jusqu'à r = r_0,
#  -> r_i = LCG(r_0), et comme Z_i = r_i * (s^c_i mod N) n'est PAS réduit mod N :
#     y_i = Z_i / r_i = s^c_i mod N  (division exacte)
#  -> Bézout sur deux c premiers entre eux : s = y_i^u * y_j^v mod N.
#
# randint(1, N) = 1 + getrandbits(2047) avec rejet tant que la valeur >= N (22 % de rejets).
# getrandbits(2047) = 64 mots de 32 bits, poids faible d'abord ; le dernier mot est décalé
# de 1 bit (on ne connaît que ses 31 bits de poids fort).
#
# Usage : python3 solve.py chall.txt
import sys, re, ast, math, random, itertools

# ---------- lecture ----------
t = open(sys.argv[1]).read()
m = re.search(r'(\d+)\s+(\d+)\s+(\d+)\s+(\[.*?\])\s+(\[.*?\])\s+(\[.*?\])', t, re.S)
a, b, N = map(int, m.groups()[:3])
Z, C, T = (ast.literal_eval(x) for x in m.groups()[3:])
K = N.bit_length()                      # 2047
W = (K + 31) // 32                      # 64 mots par tirage

# ---------- MT19937 : (dé)tempering et retour en arrière ----------
def untemper(y):
    y ^= y >> 18
    y ^= (y << 15) & 0xefc60000
    x = y
    for _ in range(5): x = y ^ ((x << 7) & 0x9d2c5680)   # inversion par itération (y reste fixe)
    y = x & 0xffffffff
    x = y
    for _ in range(3): x = y ^ (x >> 11)
    return x & 0xffffffff

def words_of(v):
    """Les 64 sorties 32 bits qui ont produit getrandbits(2047) = v (dernier mot : 31 bits connus)."""
    w = [(v >> (32 * i)) & 0xffffffff for i in range(W)]
    w[-1] = (v >> (32 * (W - 1))) << 1     # bit de poids faible du dernier mot inconnu (mis à 0)
    return w

def gen_from(state, idx):
    r = random.Random(); r.setstate((3, tuple(state) + (idx,), None)); return r

# ---------- 1) retrouver l'état à partir d'une fenêtre de 10 c consécutifs sans rejet ----------
raw = [c - 1 for c in C]
found = None
for k in range(len(C) - 11):
    win = sum((words_of(raw[k + j]) for j in range(10)), [])        # 640 mots
    unknown = [p for p in range(W - 1, 624, W)]                     # mots tronqués parmi les 624 premiers
    for bits in itertools.product((0, 1), repeat=len(unknown)):
        w = win[:624]
        for p, bt in zip(unknown, bits): w[p] |= bt
        st = [untemper(x) for x in w]
        g = gen_from(st, 624)                                       # prochaine sortie = mot 624
        nxt = [g.getrandbits(32) for _ in range(16)]                # mots 624..639 = fin de c_{k+9}
        if nxt[:15] == win[624:639] and (nxt[15] >> 1) == (win[639] >> 1):
            # contrôle fort : la suite (avec rejets) doit redonner TOUS les c suivants
            # (un contrôle sur 16 mots ne valide pas les 9 bits devinés)
            g = gen_from(st, 624); [g.getrandbits(32) for _ in range(16)]
            if [g.randint(1, N) for _ in range(len(C) - k - 10)] == C[k + 10:]:
                found = (k, st); break
    if found: break
k, st = found
print(f'état MT retrouvé (fenêtre commençant à c_{k})')

# ---------- 2) remonter le temps jusqu'à r, e, a, b ----------
# Récurrence MT : x[k+624] = x[k+397] ^ f(y),  y = MSB(x[k]) | low31(x[k+1]).
# En l'inversant, x[k+624] ^ x[k+397] redonne y, donc MSB(x[k]) et low31(x[k+1]).
# x[m] complet = MSB tiré de l'équation k=m + low31 tiré de l'équation k=m-1.
def y_of(X, k):                       # X : dict index -> mot interne (non tempéré)
    t = X[k + 624] ^ X[k + 397]
    return ((t ^ 0x9908b0df) << 1 | 1) & 0xffffffff if t & 0x80000000 else (t << 1) & 0xffffffff

def temper(y):
    y ^= y >> 11; y ^= (y << 7) & 0x9d2c5680; y ^= (y << 15) & 0xefc60000; y ^= y >> 18
    return y & 0xffffffff

X = {i: v for i, v in enumerate(st)}  # la fenêtre retrouvée : indices 0..623
for m in range(-1, -6000, -1):        # on recule mot par mot
    X[m] = (y_of(X, m) & 0x80000000) | (y_of(X, m - 1) & 0x7fffffff)

def draws_from(q, count):
    """Simule `count` appels randint(1, N) en lisant les sorties à partir du mot q."""
    out = []
    while len(out) < count:
        if q + W > 0: return None
        ws = [temper(X[q + i]) for i in range(W)]; q += W
        v = sum(w << (32 * i) for i, w in enumerate(ws[:-1])) | ((ws[-1] >> 1) << (32 * (W - 1)))
        if v < N: out.append(v + 1)
    return out

r0 = None
for q in range(-5900, 0):
    v = draws_from(q, 4)
    if v and v[2] == a and v[3] == b:
        r0, e = v[0], v[1]; print(f'r, e, a, b trouvés au mot {q} avant la fenêtre'); break
print('r_0 retrouvé, e =', e.bit_length(), 'bits')

# ---------- 3) vérifications et calcul de s ----------
R = [r0]
for _ in range(99): R.append((a * R[-1] + b) % N)
assert all(z % r == 0 for z, r in zip(Z, R)), 'r_i ne divise pas Z_i'
assert all(pow(r, e, N) == tt for r, tt in zip(R, T)), 'T_i incohérent'
print('vérifs : r_i | Z_i et r_i^e = T_i pour les 100 indices')
Y = [z // r for z, r in zip(Z, R)]
for i, j in itertools.combinations(range(100), 2):
    if math.gcd(C[i], C[j]) == 1: break
def egcd(x, y):
    """Euclide étendu itératif : renvoie (g, u, v) avec u*x + v*y = g."""
    u0, v0, u1, v1 = 1, 0, 0, 1
    while y:
        q = x // y
        x, y = y, x - q * y
        u0, u1 = u1, u0 - q * u1
        v0, v1 = v1, v0 - q * v1
    return x, u0, v0

_, u, v = egcd(C[i], C[j])                  # u*c_i + v*c_j = 1
s = pow(Y[i], u, N) * pow(Y[j], v, N) % N   # s^(u c_i + v c_j) = s  (pow gère u ou v < 0)
print(s.to_bytes((s.bit_length() + 7) // 8, 'big').decode())
