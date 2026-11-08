#!/usr/bin/env python3
# PIO Machine : "l'autre" flag du Deere Game (meme code.tar.gz que Haybales).
# C'est le flag HARD de deere_chal.py:decode_flag() : il faut key tel que
# pio_mix(key)==0x122c5bf4 (programme PIO du RP2040), puis SHA-256 + XOR.
# key trouve par brute force du PIO (cf pio_brute.c, shift-left) = 0x8661eb95.
import hashlib
key = 0x8661eb95
encoded = bytes.fromhex('9ca16ac0128e729ef5b55a9d6f9f7ffff5f97a48f508db908a86f7')
h = hashlib.sha256(int.to_bytes(key, 4, 'little')).digest()
print(bytes(a ^ b for a, b in zip(h, encoded)).decode())  # sigpwny{th3_pio_1s_4w3s0m3}
