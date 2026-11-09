---
title: "05-Grander-Finale"
ctf: "Pwny-CTF"
category: "pwn"
difficulty: "Not specified"
points: 500
techniques: ["format-string", "got-overwrite", "stack-canary", "pie-bypass", "nx-bypass"]
tools: ["gdb", "checksec", "netcat", "docker", "python"]
keywords: ["05-Grander-Finale", "Pwny-CTF", "pwn", "format-string", "got-overwrite", "stack-canary", "pie-bypass", "nx-bypass", "gdb", "checksec", "netcat", "docker", "python", "elf", "libc", "canary"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/PWN-II/05-Grander-Finale/notes.md"
---

# 05-Grander-Finale (Pwny-CTF, pwn)

## Summary
Challenge **05-Grander-Finale** from the Pwny-CTF CTF, pwn category. Main technique: format-string. Full RELRO + PIE + win-func never called -> no GOT overwrite: rewrite the saved RIP via string write format (write-what-where), after leaking PIE base and stack.

## Statement and artefacts
This challenge requires a clever arbitrary write and a leak (or two?)

```nc chal.sigpwny.com 1386```

**Author**: Kevin Higgs

**Provided files / artifacts:**
- `work/Dockerfile (file, 364 B)`
- `work/grander_finale (file, 16.9 KB)`
- `work/grander_finale_patched (file, 16.9 KB)`

## Recognition signals
- If we observe Write the full address (48 bits, think of 3 shorts with write_size="short") produces a payload of 64 to 80 bytes.
- Signal: Or fgets(name, 64, stdin) only reads 63 bytes (+ NUL). The payload is truncated -> the last %n (therefore part of the address) are not written -> failure.
- Signal: This only happened when the truncation only cut trailing zero bytes (most significant of a stack address 0x0000.).

## Resolution method
1. **Binary**

- Same code as 04: `greet()` does `printf(name)` → **format string**, in a `while(1)` loop.
- `checksec`: **Full RELRO**, **Canary**, NX, **PIE**, unstripped. `print_flag()` exists but never called.
- Why not a GOT overwrite (like 04): **Full RELRO** = GOT read-only. We therefore aim for **the return address on the stack** (write-what-where via `%n`).
- Why the canary does not interfere: we write **precisely** on the saved RIP via `%n`, without overflowing the buffer → the canary is never modified or checked against us.
- Why two leaks: **PIE** → you need the binary base (for `&print_flag`) **and** the address of the saved RIP on the stack (ASLR).

1. **Double leak** in one shipment: `%25$p %23$p`.
   - `%25$p` = a return address in `main` → `BASE = MAIN_ADDR - elf.sym["main"]`, then `elf.address = BASE` gives rebased `print_flag`.
   - `%23$p` = a stack address; the targeted saved RIP = `leak - 0x150` (offsets `%23`/`%25` and `0x150` **mapped to the Docker container**, found via GDB).
2. **Write-what-where**: `fmtstr_payload(OFFSET=10, {saved_rip_addr: print_flag}, write_size="short")` writes `print_flag` to the saved RIP of `greet`.
3. **Detonator**: at the end of `greet`, the `ret` jumps to `print_flag` → flag displayed.

Launch: `./solve.py` (hardware host/port).

2. **The reliability trap (important)**

The original script succeeded **~60-70%** of the time (confirmed in my post from 7 months ago: *"sometimes the script doesn't work"*). **Cause found**:
- Writing the **full** address (48 bits → 3 shorts with `write_size="short"`) produces a payload of **64 to 80 bytes**.
- But `fgets(name, 64, stdin)` only reads **63 bytes** (+ NUL). The payload is **truncated** → the last `%n` (therefore part of the address) are not written → failure.
- This only happened when the truncation only cut **trailing null bytes** (most significant of a stack address `0x0000...`).

**Correction (100% reliable)**: the saved RIP already contains a binary address (return to `main`); `print_flag` is in the **same PIE image**, so only the lower **32 bits differ**. We only write these **2 shorts**:
```python
payload = fmtstr_payload(OFFSET, {saved_rip_addr: PRINT_FLAG_ADDR & 0xffffffff}, write_size="short")
```
Payload **40-48 bytes**, always < 63. Verified: write low-32 → exact value of `print_flag` (GDB), and length < 64 on 2000/2000 simulated pulls.

## Solve script
Script path: [`scripts/solve.py`](scripts/solve.py)

## Flag
sigpwny{binary_expl0itat1on_m4ster}

## Lessons and reusable patterns
- Full RELRO + PIE + win-func never called -> no GOT overwrite: rewrite the saved RIP via string write format (write-what-where), after leaking PIE base and stack.
- Always compare the payload size to the read limit (fgets(buf, N) reads N-1 bytes). A format-string payload whose length depends on the randomized addresses is a time bomb -> random success rate.
- Partial overwrite: when target and destination share the PIE base, writing only the bytes which differ (here 4) shortens the payload and makes it deterministic. 16-bit writing would often suffice but breaks if a report exceeds the 16th bit -> 32 bits = safe.
- %N$p offsets and stack constants: specific to the environment (container libc). To be found by GDB on a replica, not to be guessed.
