---
title: "2-asm-leaver"
ctf: "Pwny-CTF"
category: "reverse"
difficulty: "Not specified"
points: 150
techniques: []
tools: ["pwntools", "netcat", "python"]
keywords: ["2-asm-leaver", "Pwny-CTF", "reverse", "pwntools", "netcat", "python", "syscall"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/x86_64-Assembly/2-asm-leaver/notes.md"
---

# 2-asm-leaver (Pwny-CTF, reverse)

## Summary
Challenge **2-asm-leaver** from the Pwny-CTF CTF, reverse category. Table of syscalls x86_64: exit = 60, convention rax=number, args in rdi, rsi, rdx, r10, r8, r9.

## Statement and artefacts
The program sets up the code to run a little bit of assembly! Use pwntools to send some asm to make an exit call in the child program.

`nc chal.sigpwny.com 9001`

**Provided files / artifacts:**
- `work/Dockerfile (file, 536 B)`
- `work/challenge (file, 16.2 KB)`

## Recognition signals
- Signal: No setup here: we provide the entire call. No newline trap (reads 16, does not overwrite anything).

## Resolution method
1. **The mechanism (challenge.c)**

- `fork()`: the child executes **only our code** (16 bytes, no setup/post), the parent prints the flag if the child **exit(42)**.
- `read(0, code,16)`; buffer memset to 0 initially (unused bytes = 0, never executed because we exit before).

1. `exit(42)` in syscall: `rax=60` (0x3c, number of `exit`), `rdi=42`, `syscall`.
2. `mov eax,60; mov edi,42; syscall` → 12 bytes (< 16).
3. `io.send(code)`. → `My partner exited with: 42` + flag.

## Solve script
Script path: `scripts/solve.py`

## Flag
sigpwny{leaving_so_soon_with_a_syscall?}

## Lessons and reusable patterns
- Table of syscalls x86_64: exit = 60, convention rax=number, args in rdi, rsi, rdx, r10, r8, r9.
- No setup here: we provide the entire call. No newline trap (reads 16, does not overwrite anything).
- Flag: sigpwny{leaving_so_soon_with_a_syscall?} (not submitted). Script: work/solve.py.
