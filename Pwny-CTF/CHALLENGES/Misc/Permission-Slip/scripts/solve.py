#!/usr/bin/env python3
# Permission Slip : jeu console Windows "SYSTEM BREACH" ou toutes les options
# echouent ; le hint dit d'appeler grant_admin_access(). Le flag affiche a la
# victoire est genere par une routine XOR, dechiffrable STATIQUEMENT.
# Depuis le desassemblage (fonction @0x14000ac30) :
#   cle 8 octets = dwords 0x881fc35a, 0xb1997e22  (indexes par i & 7)
#   ciphertext   = 8 dwords @[rbp-0x28] + 1 octet 0x27 @[rbp-0x8]  (33 octets)
#   flag[i] = ciphertext[i] ^ cle[i & 7]
import struct
key = b''.join(struct.pack('<I', d) for d in [0x881fc35a, 0xb1997e22])
ct = b''.join(struct.pack('<I', d) for d in
    [0xf878aa29,0xcae01055,0xbb7ca06e,0xf6c60d51,
     0xfc71f728,0xe6c61a11,0xfa2b9c69,0xdfd02111]) + bytes([0x27])
print(bytes(ct[i] ^ key[i & 7] for i in range(len(ct))).decode())
# sigpwny{4cc3ss_Gr4nt3d_W3_4r3_In}
