---
title: "Bug-Bounty-3"
ctf: "Pwny-CTF"
category: "pwn"
difficulty: "medium"
points: 200
techniques: ["ret2win", "pie-bypass", "reverse-engineering"]
tools: ["pwntools", "gdb", "objdump", "checksec", "netcat", "python"]
keywords: ["Bug-Bounty-3", "Pwny-CTF", "pwn", "ret2win", "pie-bypass", "reverse-engineering", "pwntools", "gdb", "objdump", "checksec", "netcat", "python", "elf", "pie"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/PWN-I/Bug-Bounty-3/notes.md"
---

# Bug-Bounty-3 (Pwny-CTF, pwn)

## Summary
Challenge **Bug-Bounty-3** from the Pwny-CTF CTF, pwn category. Main technique: ret2win. Ret2win: overwrite the return address with the address of a function which already gives the flag, present but never called in the normal program.

## Statement and artefacts
Less code means less bugs, right? We removed some unnecessary function calls, so it's impossible to print the flag now!

This is SUPERMEGACORP's highest bug bounty yet, at $5000!

`nc chal.sigpwny.com 1345`

**author**: Akhil

**Provided files / artifacts:**
- `work/Makefile (file, 126 B)`
- `work/challenge (file, 19.6 KB)`
- `work/challenge_patched (file, 19.6 KB)`

## Recognition signals
- Signal: Unlike Bug Bounty 1/2, the program no longer tests a neighboring variable: there is no longer any condition at all.
- Signal: The only way to get the flag is to hijack the execution flow so that it jumps into print_flag(), which exists in the binary but is never called.
- If the binary was stripped or PIE enabled: you would either have to look for the address by hand (objdump/gdb, as suggested by the clues provided), or first leak an address to calculate the real base.

## Resolution method
1. Read `challenge.c`: explicit comment — *“we don't call `print_flag` for you anymore”*. No conditions to satisfy, you must **redirect the execution**.
2. `checksec`: **No PIE** (fixed `0x400000`) + **Stripped: No** → the address of `print_flag` is both **constant** (no need for leak) and **known by its name** (`elf.sym["print_flag"]`, no need to look for it manually when disassembling).
3. Offset to return address = buffer size + `saved RBP` (always 8 bytes on x86-64) = `48 + 8 = 56`.
4. Payload: `b"A"*48 + b"B"*8 + p64(print_flag_addr)` → the first 48+8 bytes are padding (their content does not matter, `A`/`B` are just used to visually distinguish them on the stack), then `p64()` writes the exact target address of the return address.
5. `sla(b">", payload)` → at `ret` of `vuln()`, the program jumps to `print_flag()` instead of returning to `main()` → flag.

1. **Order ready**

```bash
python3 -c '
from pwn import *
elf = ELF("./challenge_patched")
io = remote("chal.sigpwny.com", 1345)
payload = b"A"*48 + b"B"*8 + p64(elf.sym["print_flag"])
io.sendlineafter(b">", payload)
print(io.recvall(timeout=2))
'
```

2. **Flaw**

```c
char name[48];
gets(name);           // no size limit
// no call to print_flag(): you have to jump in yourself
```
Unlike Bug Bounty 1/2, the program no longer tests a neighboring variable: there is **no more condition at all**. The only way to get the flag is to hijack the execution flow so that it jumps to `print_flag()`, which exists in the binary but is never called.

## Solve script
Script path: [scripts/pwny.py](scripts/pwny.py)

## Flag
sigpwny{return_to_the_basics}

## Lessons and reusable patterns
- ret2win: overwrite the return address with the address of a function which already gives the flag, present but never called in the normal program.
- Offset before the return address = buffer size + 8 bytes (the saved RBP, always 8 on x86-64) — this is systematic, not specific to this challenge.
- No PIE = fixed address = no need for leak. Stripped: No = elf.sym['name'] gives the address directly, without disassembling.
- If the binary was stripped or PIE enabled: you would either have to look for the address by hand (objdump/gdb, as suggested by the clues provided), or first leak an address to calculate the real base.
