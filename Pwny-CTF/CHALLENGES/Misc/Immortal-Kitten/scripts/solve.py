#!/usr/bin/env python3
# Immortal Kitten / "NINE LIVES" : jeu console Windows ou toutes les options tuent
# le chat (survivre 10 tours avec 9 vies). Le hint parle de patcher la variable de
# vie, mais le flag affiche a la victoire ("Here's your flag: ") est genere par une
# routine XOR qu'on peut dechiffrer STATIQUEMENT (pas besoin de jouer).
# Depuis le desassemblage (fonction @0x14000abc0) :
#   cle 8 octets  = dwords 0x38b4ff0a, 0x89721348  (indexes par i & 7)
#   ciphertext    = 9 dwords a [rbp-0x28]
#   flag[i] = ciphertext[i] ^ cle[i & 7]
import struct
key = b''.join(struct.pack('<I', d) for d in [0x38b4ff0a, 0x89721348])
ct = b''.join(struct.pack('<I', d) for d in
    [0x48d39679,0xf20b7d3f,0x0f80975d,0xe4434c77,0x0fc6cf47,
     0xe22d7f7c,0x4183c83b,0xea467b17,0x45c6cc61])
print(bytes(ct[i] ^ key[i & 7] for i in range(len(ct))).decode())
# sigpwny{Wh47?_1mM0r74l_k177y_h4ck3r}
