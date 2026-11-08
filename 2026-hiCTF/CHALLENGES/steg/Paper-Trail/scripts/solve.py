#!/usr/bin/env python3
# Paper-Trail — extrait le blob des flux TJ invisibles et le déchiffre en AES-128-CBC (clé/IV = /ID du PDF).
import re, pikepdf
from Crypto.Cipher import AES

pdf = pikepdf.open("../chall.pdf")

# 1) charge utile : la ligne TJ la plus longue de chaque flux ajouté (179,180,181 ; 182 = kerning seul)
payload = bytearray()
for n in (179, 180, 181):
    s = pdf.get_object((n, 0)).read_bytes().decode("latin1")
    lines = [[int(x) for x in re.findall(r"-?\d+", m.group(1))]
             for m in re.finditer(r"\[(.*?)\]\s*TJ", s)]
    longest = max(lines, key=len)
    # octets = tout après le préfixe "() a () b ()" (les 2 premiers nombres), le 3e inclus
    payload += bytes(x & 0xFF for x in longest[2:])

# 2) clé = /ID[0], IV = /ID[1]
id0, id1 = (bytes(x) for x in pdf.trailer["/ID"])
pt = AES.new(id0, AES.MODE_CBC, id1).decrypt(bytes(payload))
print(re.search(rb"hiCTF\{[^}]*\}", pt).group().decode())
