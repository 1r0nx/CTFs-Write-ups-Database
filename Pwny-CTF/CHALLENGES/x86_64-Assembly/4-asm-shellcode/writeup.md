---
title: "4-asm-shellcode"
ctf: "Pwny-CTF"
category: "reverse"
difficulty: "Not specified"
points: 250
techniques: ["shellcode"]
tools: ["pwntools", "netcat", "python"]
keywords: ["4-asm-shellcode", "Pwny-CTF", "reverse", "shellcode", "pwntools", "netcat", "python", "syscall"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/x86_64-Assembly/4-asm-shellcode/notes.md"
---

# 4-asm-shellcode (Pwny-CTF, reverse)

## Summary
Challenge **4-asm-shellcode** from the Pwny-CTF CTF, reverse category. Main technique: shellcode. Execve = syscall59; (rdi=ptr "/bin/sh", rsi=0, rdx=0). pwntools: asm(shellcraft.sh()).

## Statement and artefacts
The program will just run whatever you can give it. Give it some shellcode!

`nc chal.sigpwny.com 9003`

**Provided files / artifacts:**
- `work/Dockerfile (file, 536 B)`
- `work/challenge (file, 15.9 KB)`

## Recognition signals
Not specified.

## Resolution method
1. **The mechanism (challenge.c)**

- `read(0, code,64)` then `foo()` executes our code. **No closed fd, no filter.** bufsize=64.

1. Shellcode `execve("/bin/sh", 0, 0)`: `shellcraft.amd64.linux.sh()` (~44 bytes < 64).
2. stdin/stdout = our socket → interactive shell.
3. Send `cat flag.txt`. → flag.

## Solve script
Script path: `scripts/solve.py`

## Flag
sigpwny{look_i_actually_popped_a_shell!}

## Lessons and reusable patterns
- execve=syscall59; (rdi=ptr "/bin/sh", rsi=0, rdx=0). pwntools: asm(shellcraft.sh()).
- As soon as a prog executes an input without filter -> pop a shell directly.
- read(0,...) reads raw bytes: the \x00 of the shellcode passes without problem (no strcpy).
- Flag: sigpwny{look_i_actually_popped_a_shell!} (not submitted). Script: work/solve.py.
