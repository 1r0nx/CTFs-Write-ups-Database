#!/usr/bin/env python3
# Pirate Hook : jeu console Windows ou la fonction de "coordonnees" renvoie toujours
# de mauvaises valeurs ; le hint dit de HOOK la fonction. Mais le flag affiche a la
# victoire est genere par une routine XPR dechiffrable STATIQUEMENT.
# Desassemblage (fonction @0x140006230) :
#   cle 8 octets = dwords 0x544f4f42, 0x21212159  = "BOOTY!!!"
#   ciphertext   = 7 dwords @[rbp-0x28] + 1 WORD 0x5c29 @[rbp-0xc]  (30 octets)
#   flag[i] = ciphertext[i] ^ cle[i & 7]
import struct
key = b''.join(struct.pack('<I', d) for d in [0x544f4f42, 0x21212159])  # BOOTY!!!
ct = b''.join(struct.pack('<I', d) for d in
    [0x24282631,0x5a584f2e,0x623d3d76,0x584c7e31,0x673d3b1d,0x5374526d,0x60221071]) \
    + struct.pack('<H', 0x5c29)
print(bytes(ct[i] ^ key[i & 7] for i in range(len(ct))).decode())
# sigpwny{4rr6h_my_tr34sUr3_m4p}
