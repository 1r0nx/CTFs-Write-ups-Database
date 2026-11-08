# Tyco — attaque de Franklin-Reiter (messages liés, même N et même e).
#
#   t1 = r^e       mod N
#   t2 = (r + d)^e mod N     avec d connu
#
# r est racine commune de P1(x) = x^e - t1 et P2(x) = (x + d)^e - t2.
# Leur PGCD (modulo N) vaut en général (x - r) : on lit r dedans.
# e = 56263 -> polynômes de degré ~56k : il faut un PGCD rapide (FLINT).
#
# Usage : python solve.py chall.txt      (nécessite python-flint)
import sys, re
from flint import fmpz_mod_ctx, fmpz_mod_poly_ctx

# 1) Lire N, e, d, t1, t2 depuis la sortie du challenge
nums = [int(x) for x in re.findall(r'\d{5,}', open(sys.argv[1]).read())]
N, e, d, t1, t2 = nums[:5]
print(f'N : {N.bit_length()} bits, e = {e}')

# 2) Anneau des polynômes à coefficients modulo N
R = fmpz_mod_poly_ctx(fmpz_mod_ctx(N))
x = R([0, 1])                       # le polynôme "x"

P1 = x**e - t1
P2 = (x + d)**e - t2

# 3) PGCD par l'algorithme d'Euclide : (a, b) -> (b, a mod b) jusqu'à b = 0.
#    FLINT refuse son PGCD rapide si N n'est pas premier ; on fait donc la
#    boucle nous-mêmes (chaque division reste calculée en C par FLINT).
#    On rend b unitaire (coefficient dominant = 1) avant chaque division.
def poly_gcd(a, b):
    while not b.is_zero():
        lc = int(b.coeffs()[-1])
        b = b * pow(lc, -1, N)       # échoue seulement si lc partage un facteur avec N
        a, b = b, a % b
    return a

g = poly_gcd(P1, P2)
print('degré du PGCD :', g.degree())
b, a = [int(c) for c in g.coeffs()[:2]]
r = (-b * pow(a, -1, N)) % N

# 4) Vérification : on doit retrouver t1 et t2
assert pow(r, e, N) == t1 and pow(r + d, e, N) == t2
print('vérification t1/t2 : OK')
print(r.to_bytes((r.bit_length() + 7) // 8, 'big').decode())
