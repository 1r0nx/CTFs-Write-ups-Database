---
title: "3-asm-reader"
ctf: "Pwny-CTF"
category: "reverse"
difficulty: "Not specified"
points: 200
techniques: []
tools: ["netcat", "python"]
keywords: ["3-asm-reader", "Pwny-CTF", "reverse", "netcat", "python", "syscall"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/x86_64-Assembly/3-asm-reader/notes.md"
---

# 3-asm-reader (Pwny-CTF, reverse)

## Summary
Challenge **3-asm-reader** from the Pwny-CTF CTF, reverse category. Recognize: statement “flag read from a known address, write to stdout” -> write(1, addr, n). Look at which fds are closed (here 0 and 2, not 1).

## Statement and artefacts
The program reads the flag into a known address. Can you write to stdout to get the flag?

`nc chal.sigpwny.com 9002`

**Provided files / artifacts:**
- `work/Dockerfile (file, 536 B)`
- `work/challenge (file, 16.0 KB)`

## Recognition signals
Not specified.

## Resolution method
1. **The mechanism (challenge.c)**

- `mmap` fixed to `0x123412340000`, the flag is read: `read(fd, 0x123412340000, 0x28)` (40 bytes).
- Before running our code: **`close(0); close(2)`** only → **stdout (fd 1) remains open**.
- `read(0, code,48)`, we provide everything (bufsize=48).

1. `write(1, 0x123412340000, 0x28)`: `rax=1` (write), `rdi=1` (stdout), `rsi=0x123412340000`, `rdx=0x28`, `syscall`.
2. Then `exit(0)` properly (`rax=60, rdi=0, syscall`). ~36 bytes (< 48).
3. `mov rsi, 0x123412340000` = immediate 64 bits (10 bytes), short remainder. → the flag is printed on our socket.

## Solve script
Script path: `scripts/solve.py`

## Flag
sigpwny{now_we_are_reading_with_numbers}

## Lessons and reusable patterns
- Recognize: statement “flag read from a known address, write to stdout” -> write(1, addr, n). Look at which fds are closed (here 0 and 2, not 1).
- write = syscall 1; args (fd, buf, count) in (rdi, rsi, rdx).
- Flag: sigpwny{now_we_are_reading_with_numbers} (not submitted). Script: work/solve.py.
