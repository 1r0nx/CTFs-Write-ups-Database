#!/usr/bin/env python3
"""
Packets lo_l — Sombra a exfiltré un message sur la loopback (lo),
en l'envoyant à la fois en UDP et en ICMP (d'où les doublons).

Séquence des payloads (identique sur les deux canaux) :
  1) awesomesecretkey     -> clé AES (16 octets = AES-128)
  2) awesomesecretiv!     -> IV
  3) oops ignore that lol -> leurre à ignorer
  4..n) morceaux de ciphertext -> à concaténer puis déchiffrer (AES-CBC)
"""
import subprocess
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

PCAP = "sombra_hacks_packs.pcap"

def payloads(display_filter):
    """Récupère, dans l'ordre, la charge utile (hex) de chaque paquet du filtre."""
    out = subprocess.check_output(
        ["tshark", "-r", PCAP, "-Y", display_filter,
         "-T", "fields", "-e", "data.data"],
        text=True, stderr=subprocess.DEVNULL)
    lines = [l.strip() for l in out.splitlines() if l.strip()]
    # dédoublonnage des captures loopback consécutives identiques
    dedup = []
    for l in lines:
        if not dedup or dedup[-1] != l:
            dedup.append(l)
    return dedup

# On lit le canal ICMP (séquence propre : 1 message par paquet)
chunks = payloads("icmp")

key   = bytes.fromhex(chunks[0])   # awesomesecretkey
iv    = bytes.fromhex(chunks[1])   # awesomesecretiv!
decoy = bytes.fromhex(chunks[2])   # oops ignore that lol
ciphertext = b"".join(bytes.fromhex(c) for c in chunks[3:])

print(f"[i] clé   = {key!r}")
print(f"[i] IV    = {iv!r}")
print(f"[i] leurre= {decoy!r}")
print(f"[i] taille ciphertext = {len(ciphertext)} octets (mod 16 = {len(ciphertext)%16})")

cipher = AES.new(key, AES.MODE_CBC, iv)
plain = cipher.decrypt(ciphertext)
try:
    plain = unpad(plain, AES.block_size)   # retire le padding PKCS#7
except ValueError:
    pass  # si le padding n'est pas standard, on garde le brut

print("\n[+] Message déchiffré :\n")
print(plain.decode(errors="replace"))
