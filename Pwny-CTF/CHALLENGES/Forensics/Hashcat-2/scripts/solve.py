# Hashcat-2 — Pwny-CTF (script de solve)
import hashlib

TARGET = "279c061469df1eeec079f3d469bf79ade48f79ef6a5613c42715f0facb2fa618652c1762b05c2df3fd162a770f91e72bb9e7ee5eec4296aedb28dcd061edb112"

with open("sigpwny_users.txt") as f:
    usernames = [line.strip() for line in f if line.strip()]

found = False
for username in usernames:
    for i in range(10000):
        candidate = f"{username}#{i:04d}"
        h = hashlib.sha512(candidate.encode()).hexdigest()
        if h == TARGET:
            print(f"[+] Trouvé : {candidate}")
            found = True
            break
    if found:
        break

if not found:
    print("[!] Aucune correspondance trouvée.")