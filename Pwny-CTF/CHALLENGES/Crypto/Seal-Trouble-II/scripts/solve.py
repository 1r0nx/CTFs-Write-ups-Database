#!/usr/bin/env python3
# Seal-Trouble-II (Pwny-CTF, Crypto) - XOR a cle repetee, plaintext connu
#
# encrypt: ct[i] = msg[i] ^ key[i % len(key)], cle = passphrase de 5 lettres
# minuscules. message.txt = ciphertext (hex) du VRAI flag. Le flag commence par
# "sigpwny{" -> known-plaintext : key[i%5] = ct[i] ^ 's','i','g','p','w',... .
# 5 octets suffisent a recuperer toute la cle, puis on dechiffre tout.
cipher = bytes.fromhex("03010e031f1e111207001106022c111f1d36150702371d1b0d2f0e0000005149480e")
known = b"sigpwny{"

key = [cipher[i] ^ known[i] for i in range(5)]           # 5 premiers octets -> cle
assert all(cipher[i] ^ known[i] == key[i % 5] for i in range(len(known)))  # consistance
flag = bytes(cipher[i] ^ key[i % 5] for i in range(len(cipher)))
print("passphrase =", bytes(key).decode())
print(flag.decode())
