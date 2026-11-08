#!/usr/bin/env python3
# Haybales : jeu MicroPython (badge). deere_chal.py:decode_flag() a 2 flags.
# EASY : key==0xdcd8be1, encoded[i] ^ key -> flag.
# HARD : key tel que pio_mix(key)==0x122c5bf4 (programme PIO), puis SHA-256 + XOR.
import hashlib

# --- easy ---
key = 0xdcd8be1
enc = [2108351122, 1991566742, 2142157452, 984939473, 1386462089, 1855125712, 1889658065]
easy = ''.join(int.to_bytes(e ^ key, 4, 'little').decode() for e in enc)
print("EASY:", easy)              # sigpwny{m1cr0py7h0n_1s_c0ol}

# --- hard --- (key trouve par brute force du PIO, cf pio_brute.c ; shift-left)
key = 0x8661eb95
encoded = bytes.fromhex('9ca16ac0128e729ef5b55a9d6f9f7ffff5f97a48f508db908a86f7')
h = hashlib.sha256(int.to_bytes(key, 4, 'little')).digest()
hard = bytes(a ^ b for a, b in zip(h, encoded)).decode()
print("HARD:", hard)              # sigpwny{th3_pio_1s_4w3s0m3}
