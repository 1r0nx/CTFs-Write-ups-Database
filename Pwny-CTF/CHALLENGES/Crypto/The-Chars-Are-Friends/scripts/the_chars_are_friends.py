# The-Chars-Are-Friends — Pwny-CTF (script de solve)
import os

def hide(c):
    r = ord(os.urandom(1))
    return ord(c)^(r & 0xc0)

flag = 'sigpwny{????????}'

flag_arr = list(flag)
cipher_arr = [hide(c) for c in flag_arr]

print(f"{cipher_arr = }")
print("ciphertext = ", "".join([chr(c) for c in cipher_arr]))
