---
title: "Diffie-Hellman-God"
ctf: "Pwny-CTF"
category: "crypto"
difficulty: "Not specified"
points: 250
techniques: ["diffie-hellman"]
tools: ["pwntools", "netcat", "python"]
keywords: ["Diffie-Hellman-God", "Pwny-CTF", "crypto", "diffie-hellman", "pwntools", "netcat", "python"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Crypto-I/Diffie-Hellman-God/notes.md"
---

# Diffie-Hellman-God (Pwny-CTF, crypto)

## Summary
Challenge **Diffie-Hellman-God** from the Pwny-CTF CTF, crypto category. Main technique: diffie-hellman. Efficient parsing of labeled output: recvuntil(b"X = ") + recvline().strip() -> the integer.

## Statement and artefacts
Given the standard NIST parameters `g`, `p`, and also given Alices public key and your private key, compute your shared secret and send it back to the server.

`nc chal.sigpwny.com 1985`

Server `nc chal.sigpwny.com 1985`. `server.py` provided: it sends `g` and `p` **once**, then loops **1000 times** sending each round a new `b` (your private key) and `A` (Alice's public key), and waits for `shared = pow(A, b, p)` at the ` > ` prompt. An error → `exit(-1)`; 1000 correct answers → flag.

**Provided files / artifacts:**
- `work/Dockerfile (file, 240 B)`

## Recognition signals
Not specified.

## Resolution method
1. **Method (pwntools)**

1. `remote(host, port)` — opens the connection.
2. Helper `get_value(label)` = `recvuntil(label + b" = ")` then `int(recvline().strip())` → reads a labeled integer. Called once for `g` and `p`.
3. `for i in range(1000)` loop: `b = get_value(b'b')`, `A = get_value(b'A')`, `shared = pow(A, b, p)`, then **`sendlineafter(b'> ', str(shared).encode())`**.
4. After the loop, the server displays the flag (`interactive()` or `recvall`).

Script: `work/solve.py`.

## Solve script
Script path: [scripts/server.py](scripts/server.py)
Script path: [scripts/solve.py](scripts/solve.py)

## Flag
sigpwny{numbers_are_hard}

## Lessons and reusable patterns
- Efficient parsing of labeled output: recvuntil(b"X = ") + recvline().strip() -> the integer.
- Prompt without \n (input(" > ")): use sendlineafter(b'> ',...), never recvline
- Recognize the type: statement which gives private key + opposing public key and asks for the secret
- Link to [[Safe-Cracking]] (nc = data to send) and to other DH (Merkle, Not Rough) where there
