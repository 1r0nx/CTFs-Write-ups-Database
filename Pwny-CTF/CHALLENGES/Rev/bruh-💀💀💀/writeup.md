---
title: "bruh-💀💀💀"
ctf: "Pwny-CTF"
category: "reverse"
difficulty: "Not specified"
points: 1000
techniques: ["xor-cipher", "rop", "reverse-engineering", "vm-reverse"]
tools: ["pwntools", "python"]
keywords: ["bruh-💀💀💀", "Pwny-CTF", "reverse", "xor-cipher", "rop", "reverse-engineering", "vm-reverse", "pwntools", "python", "elf", "xor", "syscall", "oracle"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Rev/bruh-💀💀💀/notes.md"
---

# bruh-💀💀💀 (Pwny-CTF, reverse)

## Summary
Challenge **bruh-💀💀💀** from the Pwny-CTF CTF, reverse category. Main technique: xor-cipher. Weird machine / ROP-VM: rsp pointing in.data + micro-gadgets op;ret = an ROP interpreter. Disassemble.text lists the ISA (gadgets);.data is the bytecode. Distinctive sign: ridiculous.text, immense.data, hand rewriting rsp.

## Statement and artefacts
This is an RE chal, not pwn. Usage:./bruh

**Provided files / artifacts:**
- `work/bruh (file, 1.1 MB)`

## Recognition signals
- If we observe ELF not stripped but only one useful function, think of main. Tiny.text (~0x215 B) vs huge.data (~1.1 MB).
- Signal: main: lea rax,0x414028; mov rsp, rax; ret -> place rsp in.data then ret. So.data is a giant ROP chain (~131072 pointers) which chains micro-gadgets “1 operation; ret” (pop rX, mov [rbx], rax, add, xor, cmp, syscall…). It is a program compiled in ROP.
- Signal: Execution trap: it reads the flag via read(fd=1, …) — from stdout, not stdin. In pipe -> EBADF and crash; you need a PTY (process(…, stdin=PTY, stdout=PTY, stderr=PTY)).

## Resolution method
1. **Method (emulation + oracle)**

1. **Emulate** with Unicorn: load segments, start at `main` (0x401110), implement syscalls `read`/`write`/`exit` (read ⇒ provide candidate bytes; write ⇒ collect output).
2. **Observe**: with a test input, the final decision is a `cmp` of a calculated value vs a constant, and above all the check is **sequential** — it stops at the **1st false byte**.
3. **Oracle**: count the comparisons executed (`cmp rax, rbx`@0x40111f / `cmp rcx, rbx`@0x401123). This counter **increases with the length of the correct prefix** (e.g. `"AAAA…"`→175, `"sigpwny{…"`→319). One run ≈ 0.01 s.
4. **Gluttonous**: for each position, try all the printable characters, keep the one that **maximizes** the counter; start again at the next position until `Correct flag!`. Length 24, prefix `sigpwny{`, final `}`.

See `work/solve.py` (Unicorn + gluttonous emulator, standalone). Live validation: `process("./bruh", stdin=PTY, stdout=PTY, stderr=PTY)`.

2. **Recognize**

- ELF not stripped but **only one** useful function: `main`. `.text` tiny (~0x215 B) vs `.data` **huge (~1.1 MB)**.
- `main`: `lea rax,0x414028; mov rsp, rax; ret` → places `rsp` **in `.data`** then `ret`. So `.data` is a giant **ROP chain** (~131072 pointers) which chains micro-gadgets “1 operation; ret” (`pop rX`, `mov [rbx], rax`, `add`, `xor`, `cmp`, `syscall`…). It is a program compiled in ROP.
- Execution trap: it reads the flag via `read(fd=1, …)` — **from stdout**, not stdin. In pipe → `EBADF` and crash; you need a **PTY** (`process(…, stdin=PTY, stdout=PTY, stderr=PTY)`).

## Solve script
Script path: `scripts/solve.py`

## Flag
sigpwny{let5_r0p_n_r011}

## Lessons and reusable patterns
- Weird machine / ROP-VM: rsp pointing in.data + micro-gadgets op;ret = an ROP interpreter. Disassemble.text lists the ISA (gadgets);.data is the bytecode. Distinctive sign: ridiculous.text, immense.data, hand rewriting rsp.
- When static is out of scope, emulate: Unicorn transforms binary into a run(input) -> (output, metrics) function. We use it as an oracle.
- Sequential check = greedy search: a channel (number of comparisons / instructions executed) which increases with each correct byte allows the flag to be reconstructed position by position (linear), without understanding the internal algorithm. Same spirit as the Flag Vault timing attack, but the “time” here is an emulation counter.
- Be careful with fd: reading on fd=1 (stdout) instead of 0 breaks the pipes -> PTY mandatory to drive the real binary.
