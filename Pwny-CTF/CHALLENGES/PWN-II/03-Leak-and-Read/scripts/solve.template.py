# 03-Leak-and-Read — Pwny-CTF (script de solve)
from pwn import *

# Useful functions:
# int(string, 16)
# - convert hexadecimal string into integer
# p64(address)
# - convert 64-bit integer address into little endian bytes
# response.split(b"...")
# - split response on "..." (change to your desired delimiter)
# - if you're familiar with python string processing, feel free to use other functions :)

# Check the slides for information on how to get and use a leak!

p = process("./leak_and_read")

p.sendlineafter(b"What is your name? ", b"Kevin") # change "Kevin" to your malicious input
response = p.recvuntil(b'\n')
print(response)

# do something with response

p.sendlineafter(b"What is your name? ", b"Richard") # change "Richard" to your malicious input
response = p.recvuntil(b'\n')
print(response)

p.interactive()
