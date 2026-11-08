#!/usr/bin/env python3
# VIM Quiz : quiz interactif sur nc chal.sigpwny.com 5094. 4 questions.
# Format reponse : combinaison avec tiret (Ctrl+[ => "c-[").
from pwn import *
import re
context.log_level = 'error'

table = [
    ("enter insert mode", "i"),
    ("end of the line", "$"),
    ("repeat the last command", "."),
    ("equivalent to escape", "c-["),
]
def answer(q):
    ql = q.lower()
    for k, v in table:
        if k in ql:
            return v
    return None

r = remote('chal.sigpwny.com', 5094)
buf = r.recvuntil(b"? ", timeout=8).decode(errors='replace')
while True:
    m = re.findall(r'\d+\.\s*([^?]+\?)', buf, re.S)
    q = (m[-1] if m else buf).strip().replace("\n", " ")
    a = answer(q)
    if a is None:
        print("INCONNU:", q); break
    r.sendline(a.encode())
    try:
        buf = r.recvuntil(b"? ", timeout=5).decode(errors='replace')
    except EOFError:
        tail = r.clean(timeout=2).decode(errors='replace')
        print(re.search(r'sigpwny\{[^}]*\}', tail).group(0))  # flag
        break
