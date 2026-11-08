#!/usr/bin/env python3
# bruh 💀💀💀 — reverse d'un checker compile en "weird machine" ROP.
#
# Le binaire : .text minuscule (~40 micro-gadgets "1 op ; ret") + .data geante (~1 Mo).
# main fait : rsp = 0x414028 (dans .data) ; ret.  => .data EST une chaine ROP qui pilote
# ces gadgets : c'est une VM/programme compile en ROP. Il lit le flag octet par octet via
# read(fd=1) (depuis stdout, pas stdin -> il faut un PTY en vrai) et le verifie.
#
# Reverse statique impossible (131072 gadgets). On EMULE avec Unicorn :
#   - on implemente les syscalls read/write/exit,
#   - le check est SEQUENTIEL (s'arrete au 1er octet faux),
#   - donc le nombre de comparaisons executees (cmp rax,rbx @0x40111f / rcx,rbx @0x401123)
#     croit avec la longueur du prefixe correct  => oracle pour une recherche gloutonne.
# On fixe chaque octet au candidat qui maximise ce compteur, jusqu'a "Correct flag!".
#
#   FLAG = sigpwny{let5_r0p_n_r011}   ("let's rop n roll")

import struct, string
from unicorn import *
from unicorn.x86_const import *

RAW = open("bruh", "rb").read()

# --- charge les segments PT_LOAD ---
e_phoff = struct.unpack_from("<Q", RAW, 0x20)[0]
e_phent = struct.unpack_from("<H", RAW, 0x36)[0]
e_phnum = struct.unpack_from("<H", RAW, 0x38)[0]
SEGS = []
for i in range(e_phnum):
    o = e_phoff + i * e_phent
    if struct.unpack_from("<I", RAW, o)[0] != 1:       # PT_LOAD
        continue
    po = struct.unpack_from("<Q", RAW, o + 8)[0]
    pv = struct.unpack_from("<Q", RAW, o + 16)[0]
    pf = struct.unpack_from("<Q", RAW, o + 32)[0]
    pm = struct.unpack_from("<Q", RAW, o + 40)[0]
    SEGS.append((pv, po, pf, pm))
LO = min(s[0] for s in SEGS)
HI = max(s[0] + s[3] for s in SEGS)
BASE = LO & ~0xFFF
SIZE = (((HI + 0x200000) & ~0xFFF) - BASE)

CMP_RAX = 0x40111F   # cmp rax,rbx ; ret
CMP_RCX = 0x401123   # cmp rcx,rbx ; ret


def run(flag):
    """Emule bruh avec `flag` en entree. Renvoie (output, nb_de_comparaisons)."""
    uc = Uc(UC_ARCH_X86, UC_MODE_64)
    uc.mem_map(BASE, SIZE)
    for v, o, fsz, _ in SEGS:
        uc.mem_write(v, RAW[o:o + fsz])
    inq = list(flag.encode() + b"\n")
    out = bytearray()
    cmps = [0]

    def syscall(uc, _):
        rax = uc.reg_read(UC_X86_REG_RAX)
        rsi = uc.reg_read(UC_X86_REG_RSI)
        rdx = uc.reg_read(UC_X86_REG_RDX)
        if rax == 0:                                   # read
            for k in range(rdx):
                uc.mem_write(rsi + k, bytes([inq.pop(0) if inq else 0]))
            uc.reg_write(UC_X86_REG_RAX, rdx)
        elif rax == 1:                                 # write
            out.extend(uc.mem_read(rsi, rdx))
            uc.reg_write(UC_X86_REG_RAX, rdx)
        elif rax in (60, 231):                         # exit
            uc.emu_stop()
        else:
            uc.reg_write(UC_X86_REG_RAX, 0)

    uc.hook_add(UC_HOOK_INSN, syscall, None, 1, 0, UC_X86_INS_SYSCALL)
    uc.hook_add(UC_HOOK_CODE, lambda *a: cmps.__setitem__(0, cmps[0] + 1),
                None, CMP_RAX, CMP_RCX + 1)
    try:
        uc.emu_start(0x401110, 0, count=300_000_000)   # start at main
    except UcError:
        pass
    return bytes(out), cmps[0]


def solve():
    CS = ("sigpwny_{}" + string.ascii_letters + string.digits + "!?-.:@#$%^&*()+=/<>[]")
    CS = list(dict.fromkeys(CS))                       # dedup, garde l'ordre
    flag = list("sigpwny{" + "A" * 15 + "}")           # longueur 24, '}' final
    for i in range(8, len(flag) - 1):
        best, best_cc = None, -1
        for ch in CS:
            flag[i] = ch
            out, cc = run("".join(flag))
            if b"Incorrect" not in out:                # succes complet -> fini
                return "".join(flag)
            if cc > best_cc:
                best_cc, best = cc, ch
        flag[i] = best
    return "".join(flag)


if __name__ == "__main__":
    print(solve())
