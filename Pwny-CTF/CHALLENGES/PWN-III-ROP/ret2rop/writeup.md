---
title: "ret2rop"
ctf: "Pwny-CTF"
category: "pwn"
difficulty: "Not specified"
points: 400
techniques: ["format-string", "buffer-overflow", "ret2libc", "rop", "stack-canary", "pie-bypass", "nx-bypass"]
tools: ["checksec", "netcat", "python"]
keywords: ["ret2rop", "Pwny-CTF", "pwn", "format-string", "buffer-overflow", "ret2libc", "rop", "stack-canary", "pie-bypass", "nx-bypass", "checksec", "netcat", "python", "libc", "canary", "pie"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/PWN-III-ROP/ret2rop/notes.md"
---

# ret2rop (Pwny-CTF, pwn)

## Summary
Challenge **ret2rop** from the Pwny-CTF CTF, pwn category. Main technique: format-string. Recognize: several leaks necessary before attacking = “all protections”. The code often comments on the procedure to follow (here literally: “leak the canary… and a libc address”).

## Statement and artefacts
Can you pwn this program and read flag.txt? This binary has full protections 😳

`nc chal.sigpwny.com 1378`

**author**: Nathan

- `challenge.c`: two `gets(answer)` on `char answer[32]` + one `printf(answer)` in between.
- Protections: **Full RELRO + Canary + NX + PIE** (all activated).
  - `printf(answer)` → **format string** (leak).
  - `gets(answer)` → **unlimited buffer overflow** (ROP).

**Provided files / artifacts:**
- `work/Dockerfile (file, 550 B)`
- `work/challenge (file, 19.3 KB)`
- `work/challenge_patched (file, 24.0 KB)`
- `work/ld-2.31.so (library, 187.0 KB)`
- `work/libc-2.31.so (library, 7.1 MB)`
- `work/libc.so.6 (file, 7.1 MB)`

## Recognition signals
- Signal: PIE activated but no need to leak the binary base: the entire ROP chain lives in libc -> a single libc leak is enough. The PIE only interferes if you want binary addresses.

## Resolution method
1. **Reconnaissance** — `checksec` (via `pwny.py`) → Full RELRO/Canary/NX/PIE; libc-2.31 provided → `pwninit` (patched binary + ld).
2. **Find indexes of format string** — `offset_browser(prompt=b"it.", reconnect=True)` → `%11$p` = canary, `%13$p` = return address in `__libc_start_main`.
3. **Leak** — `payload = b"%11$p %13$p"` then analysis:
   - `canary_value = leak[0]`
   - `libc_start_main = leak[1] - 0xf3` → start of the function (the leaked address is `__libc_start_main+243`).
   - `libc.address = libc_start_main - libc.sym["__libc_start_main"]` → **libc base rebased**.
4. **Gadgets** — `rop = ROP([libc])` → `ret`, `pop rdi; ret`; `/bin/sh` via `libc.search`, `system` via `libc.sym`.
5. **Payload BOF** — `b"A"*40 + p64(canary) + b"C"*8 + [ret, pop_rdi, /bin/sh, system]`
   - 40 B padding → **canary rewritten identically** (otherwise `__stack_chk_fail`) → 8 B saved RBP → ROP.
   - `ret` head alignment (otherwise `movaps` in `system` → SIGSEGV).
6. **Shell** → `cat flag.txt`.

## Solve script
Script path: `scripts/pwny.py`

## Flag
sigpwny{congratulations_for_figuring_that_one_out!}

## Lessons and reusable patterns
- Recognize: several leaks necessary before attacking = “all protections”. The code often comments on the procedure to follow (here literally: “leak the canary… and a libc address”).
- PIE activated but no need to leak the binary base: the entire ROP chain lives in libc -> a single libc leak is enough. The PIE only interferes if you want binary addresses.
- Canary = large value whose least significant byte is 00 (visible in the leak 0x...00).
- Equivalent Plan B (in work/solve.py): execve("/bin/sh",0,0) via syscall (pop rax=59, pop rdi/rsi/rdx, syscall) instead of system.
- Twin of Libc ROP (same technique, same offsets %11$/%13$).
