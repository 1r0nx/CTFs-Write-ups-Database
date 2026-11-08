#!/usr/bin/env python3
# VIM Golf : creer out.txt avec "N hello" (N=1..9) en <=40 frappes (<=80 hex).
# Astuce : une macro qui duplique la ligne (Yp) et incremente le nombre (Ctrl-A).
#   i1 hello<Esc>  -> "1 hello"
#   qq Yp <C-a> q  -> macro : duplique + incremente (cree la ligne "2 hello")
#   7@q            -> repete 7x -> lignes 3..9
#   :wq out.txt<CR>
from pwn import remote
context_hex = (b"i1 hello\x1b" + b"qqYp\x01q" + b"7@q" + b":wq out.txt\r").hex()
# 30 frappes = 60 hex chars
r = remote('chal.sigpwny.com', 5092)
r.sendlineafter(b"here:", context_hex.encode())
print(r.recvall(timeout=10).decode(errors='replace'))
# -> sigpwny{v1m_i5_qu17e_c0mp4c7}
