# Diffie-Hellman-God — Pwny-CTF (script de solve)
from pwn import *

context.log_level = 'info'

HOST, PORT = "chal.sigpwny.com", 1985

io = remote(HOST, PORT)

def get_value(val):
    io.recvuntil(val + b" = ")
    return int(io.recvline().strip())

g = get_value(b'g')
p = get_value(b'p')

for i in range(1,1001):
    b = get_value(b'b')
    A = get_value(b'A')

    print(f"Solving {i} question ...")
    shared_secret = pow(A,b,p)
    io.sendlineafter(b'> ', str(shared_secret).encode())

io.interactive()