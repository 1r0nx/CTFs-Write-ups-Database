#!/usr/bin/env python3
# Safe-Cracking (Pwny-CTF, Crypto) - 3 petits problemes Diffie-Hellman
# Chaque reponse = une partie de la combinaison du coffre.
#
# Rappel DH : public g,p ; prive a,b ; public A=g^a, B=g^b ; secret s=g^(ab)=A^b=B^a.

# 1) p=17,g=3, Anna priv=5, Beatrice priv=11 -> secret partage = g^(5*11) mod 17
ans1 = pow(3, 5 * 11, 17)

# 2) p=157,g=2, Anna priv=67 -> cle PUBLIQUE d'Anna = g^67 mod 157
ans2 = pow(2, 67, 157)

# 3) p=3042161,g=5, secret s=2417097, Beatrice priv=73 -> trouver Anna priv a
#    s = (g^b)^a mod p -> log discret base (g^b), brute (p petit)
p3, g3, s, b3 = 3042161, 5, 2417097, 73
Bpub = pow(g3, b3, p3)
cur, ans3 = 1, None
for i in range(1, p3):
    cur = (cur * Bpub) % p3
    if cur == s:
        ans3 = i
        break

print("Partie 1 (secret)      :", ans1)   # 11
print("Partie 2 (Anna public) :", ans2)   # 112
print("Partie 3 (Anna priv)   :", ans3)   # 81
# La combinaison = ces 3 valeurs. Format exact du flag a confirmer cote plateforme
# (ex. sigpwny{11_112_81}).
print("combinaison =", ans1, ans2, ans3)
