#!/usr/bin/env python3
# main.py : le flag (25 car.) est mélangé par shuffle() puis, pour chaque préfixe, hash(prefixe)
# est comparé à correct[i]. hash est un ROLLING HASH cumulatif :
#   h0 = 0x60e647a3 ; h_i = (h_{i-1}*31 + ord(c_i)) & 0xffffffff
# donc correct[i] = h après i+1 caractères -> on récupère chaque caractère (mélangé) :
#   ord(c_i) = (correct[i] - correct[i-1]*31) & mask     (c_0 avec h0)
# Le time.sleep(0.1) ne sert qu'à rendre le brute-force prévu ("try every letter") lent : inutile ici.
# Reste à inverser shuffle(), déterministe (seed global fixe, indépendant du contenu).

correct = [0xbbe2ad2d, 0xc072f8e7, 0x4dec2458, 0x6f986725, 0x83747ded,
           0xeb1b402e, 0x784cc60b, 0x914bfb88, 0x983375ee, 0x6e3b4846,
           0x592dc0b1, 0xcc8a55e8, 0xc4c0678a, 0xd34c8a2f, 0x9644bc1a,
           0x3252c798, 0x18062bd6, 0xe8bf4f1d, 0x2f2a94e2, 0xb6280791,
           0x0ed8eb02, 0xcc4475aa, 0xbc4a3ffb, 0xccfdbfcc, 0xd2ba3a2b]
MASK = 0xffffffff
H0 = 0x60e647a3
N = len(correct)

seed = 0
def randint(to):
    global seed
    seed += 0x1337
    for _ in range(10):
        seed = (seed * 0x343fd + 0x269ec3) & MASK
    return seed % to

def shuffle(s):
    for i in range(len(s) - 1, 0, -1):
        j = randint(i + 1)
        s[i], s[j] = s[j], s[i]
    return s


def main():
    # 1) rolling hash inversé -> caractères dans l'ordre mélangé
    shuffled, prev = [], H0
    for i in range(N):
        shuffled.append(chr((correct[i] - prev * 31) & MASK))
        prev = correct[i]

    # 2) permutation du shuffle (indépendante du contenu) : perm[i] = indice d'origine en position i
    perm = shuffle(list(range(N)))
    orig = [None] * N
    for i in range(N):
        orig[perm[i]] = shuffled[i]
    print("Flag:", "".join(orig))


if __name__ == "__main__":
    main()
