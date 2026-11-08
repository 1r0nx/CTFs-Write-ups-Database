#!/usr/bin/env python3
# storeExamine() option 5 : la saisie est transformée N fois par
#   T(x) = randomize3(randomize2(randomize3(x)))
# puis comparée à `data` (qui se termine par `flag`). flag[] et data[] sont donc des
# valeurs DÉJÀ transformées N fois ; pour lire le flag on inverse T sur chaque élément.
#
# N = nombre d'itérations de `while c != 60: c = (c*0x1337)%2**32` (énorme, discret-log).
# Inutile de le calculer : T est une bijection de PETIT ORDRE sur le domaine des valeurs,
# donc on applique l'inverse T^-1 jusqu'à retomber sur de l'ASCII lisible (ici 2 pas).

flag = [1623, 3158, 598, 1367, 599, 2902, 3159, 3671, 342, 1363, 2902, 343, 2645, 3926, 87,
        1623, 343, 2645, 2390, 1363, 1363, 3670, 2645, 1878, 87, 3159, 2645, 1878, 87, 3159,
        2645, 1878, 87, 3159, 2135]

randomize2 = lambda x: (x & 0xF) << 4 | (x & 0xF0) << 4 | (x & 0xF00) >> 8 | x & ~0xFFF
randomize3 = lambda x: x ^ 24 ^ 1 ^ 73 ^ 5
# randomize2 fait tourner les 3 nibbles bas (n0->n1->n2->n0) ; l'inverse tourne dans l'autre sens
derand2 = lambda x: (x & 0xF0) >> 4 | (x & 0xF00) >> 4 | (x & 0xF) << 8 | x & ~0xFFF
# randomize3 (XOR) est son propre inverse
Tinv = lambda x: randomize3(derand2(randomize3(x)))


def main():
    assert all(derand2(randomize2(v)) == v for v in range(4096))   # derand2 inverse bien randomize2
    cur = list(flag)
    for n in range(1, 5000):
        cur = [Tinv(x) for x in cur]
        if all(0x20 <= c <= 0x7e for c in cur) and bytes(cur).startswith(b"sigpwny{"):
            print(f"T^-1 appliqué {n} fois")
            print("Flag:", bytes(cur).decode())
            return
    print("non trouvé")


if __name__ == "__main__":
    main()
