---
title: "Bug-Bounty-6"
ctf: "Pwny-CTF"
category: "pwn"
difficulty: "Not specified"
points: 350
techniques: ["format-string", "shellcode", "stack-canary", "pie-bypass", "nx-bypass"]
tools: ["gdb", "checksec", "netcat", "python"]
keywords: ["Bug-Bounty-6", "Pwny-CTF", "pwn", "format-string", "shellcode", "stack-canary", "pie-bypass", "nx-bypass", "gdb", "checksec", "netcat", "python", "libc", "canary", "aslr", "pie"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/PWN-I/Bug-Bounty-6/notes.md"
---

# Bug-Bounty-6 (Pwny-CTF, pwn)

## Summary
Challenge **Bug-Bounty-6** from the Pwny-CTF CTF, pwn category. Main technique: format-string. Printf(user_entry) without "%s" = format string, even without %n visible: %p is enough to read everything on the stack.

## Statement and artefacts
Is this even worth it anymore...

Bug bounty: $0.01

`nc chal.sigpwny.com 1348`

**author**: Akhil

**Provided files / artifacts:**
- `work/Makefile (file, 131 B)`
- `work/challenge (file, 18.8 KB)`
- `work/challenge_patched (file, 18.8 KB)`

## Recognition signals
- Signal: fgets(buf, N, stdin) is only safe if N <= sizeof(buf) declared; here N=64 on an array of 32 = silent overflow to the neighboring variable.

## Resolution method
1. Read `challenge.c` — `printf(name)` without imposed format (`"%s"`) → format string; just after, `fgets(info, 64, stdin)` while `info` is only 32 bytes → hidden overflow even if `fgets` looks safe.
2. `checksec` → no canary, stack **executable** (RWX), PIE active but unimportant (we only leak the stack).
3. Name sent = `%p.` × 10 → leaking several values from the stack, including a stack address in the first position.
4. `info_name_addr = leak + 0x2140`: ASLR randomizes the **base** of the stack, not the **distance** between two variables, so a fixed offset (found by reverse/GDB) is enough to find the address of the buffer `name` at each connection.
5. Second entry (`info[32]`, but `fgets` accepts 64): `shellcode` (execve `/bin/sh`) + padding up to 32 bytes + 8 bytes to return address + `p64(info_name_addr)` → the `ret` jumps into the shellcode placed on the stack.
6. `conn.interactive()` → shell → `cat flag.txt`.

## Solve script
Script path: [scripts/pwny.py](scripts/pwny.py)

## Flag
sigpwny{i_shoulda_used_rust_instead}

## Lessons and reusable patterns
- printf(user_entry) without "%s" = format string, even without %n visible: %p is enough to read everything on the stack.
- fgets(buf, N, stdin) is only safe if N <= sizeof(buf) declared; here N=64 on an array of 32 = silent overflow to the neighboring variable.
- No canary + executable stack = the most direct ret2shellcode: leak a stack address, overflow until return, jump in. No need for libc or bypassing a canary.
