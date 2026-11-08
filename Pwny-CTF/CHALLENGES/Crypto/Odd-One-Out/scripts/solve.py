#!/usr/bin/env python3
# Odd One Out (Pwny-CTF, Crypto) - cryptopals set 1 ch.8
#
# AES-ECB chiffre chaque bloc de 16 octets INDEPENDAMMENT avec la meme cle :
# deux blocs de plaintext identiques donnent deux blocs de ciphertext identiques.
# Un plaintext anglais (ou avec des repetitions) trahit donc l'ECB par des blocs
# de 16 octets DUPLIQUES dans le ciphertext. On cherche l'unique ligne qui en a.
import sys

best = None
for line in open("chal.txt"):
    h = line.strip()
    if not h:
        continue
    b = bytes.fromhex(h)
    blocks = [b[i:i+16] for i in range(0, len(b), 16)]
    if len(blocks) != len(set(blocks)):      # au moins un bloc repete
        best = h
        print(f"[+] {len(blocks)-len(set(blocks))} bloc(s) duplique(s)")

print("ciphertext AES-ECB :")
print(best)
# NB : la description dit que le flag EST ce hex. A soumettre tel quel, ou wrappe
# sigpwny{...} selon la plateforme (ne pas deviner le wrapper a l'aveugle).
