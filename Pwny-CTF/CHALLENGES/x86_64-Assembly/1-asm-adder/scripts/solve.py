#!/usr/bin/env python3
# 1 - asm adder : setup met rax=0x3c (exit), rdi=0x10 (16), puis NOTRE code, puis syscall.
# Le parent imprime le flag si l'enfant exit(112). Il faut donc rdi=112 => add rdi, 112-16 = 0x60.
# Le dernier octet lu (le \n) est remis a 0x90 (nop), donc on envoie les octets + newline.
from pwn import *
context.arch = "amd64"
context.log_level = "warning"

HOST, PORT = "chal.sigpwny.com", 9000
code = asm("add rdi, 0x60")   # 48 83 c7 60  (4 octets, tient dans bufsize=8)

io = remote(HOST, PORT)
io.recvuntil(b"Give me code:")
io.send(code + b"\n")
print(io.recvall(timeout=5).decode(errors="replace"))
