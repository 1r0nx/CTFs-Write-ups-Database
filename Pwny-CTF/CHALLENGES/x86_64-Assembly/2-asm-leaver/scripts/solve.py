#!/usr/bin/env python3
# 2 - asm leaver : on fournit TOUT le code (16 octets), aucun setup/post.
# Parent imprime le flag si l'enfant exit(42). On ecrit donc l'appel exit(42) complet :
#   rax=60 (exit), rdi=42, syscall.
from pwn import *
context.arch = "amd64"
context.log_level = "warning"

HOST, PORT = "chal.sigpwny.com", 9001
code = asm("mov eax, 60; mov edi, 42; syscall")   # 12 octets, tient dans 16

io = remote(HOST, PORT)
io.recvuntil(b"Give me code:")
io.send(code)
print(io.recvall(timeout=5).decode(errors="replace"))
