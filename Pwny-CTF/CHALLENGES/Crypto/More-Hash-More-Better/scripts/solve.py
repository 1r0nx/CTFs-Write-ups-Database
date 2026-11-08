# More-Hash-More-Better — Pwny-CTF (script de solve)
import hashlib

with open('../hashes.txt', 'r') as f:
    hashes = [line.strip() for line in f]
flag = []

for hash in hashes:
    for c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUV{}0123456789_":
        h = hashlib.sha256()
        h.update(c.encode())
        if h.hexdigest() == hash:
            flag.append(c)
            break
print("".join(flag))