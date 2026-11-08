#!/usr/bin/env python3
# PAD-PAD-PAD (Pwny-CTF, Crypto-I) - many-time pad (one-time pad REUTILISE)
#
# 11 messages XORes avec la MEME cle aleatoire (os.urandom(1024)). Un OTP n'est
# sur que s'il est utilise UNE fois : reutilise, c'est un "many-time pad" cassable.
# Cle reutilisee => pour chaque COLONNE j, on a plusieurs (ct_i[j]) = m_i[j] ^ key[j].
# Les plaintext sont de l'anglais : on cherche, pour chaque colonne, l'octet de cle
# qui rend tous les m_i[j] imprimables et "le plus anglais possible" (scoring).
import ast

cts = [bytes.fromhex(h) for h in ast.literal_eval(open("message.txt").read())]
L = max(map(len, cts))

def score(o):                    # plausibilite "texte anglais" d'un octet
    if o == 32: return 8         # espace (tres frequent)
    if 97 <= o <= 122: return 6  # minuscule
    if 65 <= o <= 90: return 3   # majuscule
    if o in (39, 44, 46, 33, 63, 95, 45, 58, 59, 123, 125) or 48 <= o <= 57: return 2
    return -100                  # non imprimable -> cle rejetee

key = bytearray(L)
for col in range(L):
    present = [c[col] for c in cts if col < len(c)]
    best, bs = 0, -10**9
    for k in range(256):
        s = sum(score(b ^ k) for b in present)
        if s > bs:
            bs, best = s, k
    key[col] = best

for i, c in enumerate(cts):
    print(i, bytes(c[j] ^ key[j] for j in range(len(c))))

# Le message 10 est le flag. Quelques colonnes peu couvertes sortent bruitees ;
# on les corrige avec le crib "sigpwny{" en tete et le contexte (MTV Cribs,
# relance en 2021). La cle ainsi deduite rend TOUS les autres messages anglais,
# ce qui valide :
print("\nFLAG = sigpwny{they_rebooted_mtv_cribs_in_2021}")
