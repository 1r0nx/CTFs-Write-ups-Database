---
title: "1-asm-adder"
ctf: "Pwny-CTF"
category: "reverse"
difficulty: "Not specified"
points: 100
techniques: []
tools: ["pwntools", "netcat", "python"]
keywords: ["1-asm-adder", "Pwny-CTF", "reverse", "pwntools", "netcat", "python", "syscall"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/x86_64-Assembly/1-asm-adder/notes.md"
---

# 1-asm-adder (Pwny-CTF, reverse)

## Summary
Challenge **1-asm-adder** from the Pwny-CTF CTF, reverse category. Recognize: service which concatenates setup + your code + syscall and reads the exit code -> you complete an operation, not all the code.

## Statement and artefacts
The program sets up the code to run a little bit of assembly! Use pwntools to send some asm to fix the exit call in the child program.

```
from pwn import *

# p = process("./challenge")
p = remote('chal.sigpwny.com', 9000)
"""
0:  ?? ?? ?? ??             add    ??, ?????
"""
p.sendline('\x??\x??\x??\x??')
p.interactive()
```

`nc chal.sigpwny.com 9000`

**Provided files / artifacts:**
- `work/Dockerfile (file, 536 B)`
- `work/challenge (file, 16.2 KB)`

## Recognition signals
- Signal: Trap: the last byte (newline) is overwritten by a nop -> do not count on it; keep the payload short.

## Resolution method
1. **The mechanism (challenge.c)**

- `fork()`: child executes `setup + OUR_code + syscall`, parent prints flag if child **exit(112)**.
- setup: `mov al,0x3c` (rax=0x3c=exit), `mov di,0x10` (rdi=16). post: `syscall`.
- Reading: `read(0, code,8)` then the **last byte read (the `\n`) is handed over to `0x90` (nop)** → send the bytes + newline.

1. You need rdi=112, setup sets it to 16 → add `112-16 = 96 = 0x60`.
2. `add rdi, 0x60` → `48 83 c7 60` (4 bytes, fits in bufsize=8).
3. `io.send(code + b"\n")` after `Give me code:`. → `My partner exited with: 112` + flag.

## Solve script
Script path: `scripts/solve.py`

## Flag
sigpwny{look_mom_im_adding_numbers}

## Lessons and reusable patterns
- Recognize: service which concatenates setup + your code + syscall and reads the exit code -> you complete an operation, not all the code.
- Trap: the last byte (newline) is overwritten by a nop -> do not count on it; keep the payload short.
- Flag: sigpwny{look_mom_im_adding_numbers} (not submitted). Script: work/solve.py.
