---
title: "5-asm-modifier"
ctf: "Pwny-CTF"
category: "reverse"
difficulty: "Not specified"
points: 500
techniques: ["shellcode", "pie-bypass"]
tools: ["netcat", "python"]
keywords: ["5-asm-modifier", "Pwny-CTF", "reverse", "shellcode", "pie-bypass", "netcat", "python", "aslr", "syscall"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/x86_64-Assembly/5-asm-modifier/notes.md"
---

# 5-asm-modifier (Pwny-CTF, reverse)

## Summary
Challenge **5-asm-modifier** from the Pwny-CTF CTF, reverse category. Main technique: shellcode. The buffer is RWX to a known address; we write the byte-pair 0f 05 (syscall) at runtime to bypass a static filter.

## Statement and artefacts
I prevent you from using syscall by checking if `\x0f\x05` is in your input. But you know where your shellcode is stored, can you bypass it?

`nc chal.sigpwny.com 9004`

**Provided files / artifacts:**
- `work/Dockerfile (file, 536 B)`
- `work/challenge (file, 15.9 KB)`

## Recognition signals
- Signal: the buffer is RWX at a known address; we write the byte-pair 0f 05 (syscall) at runtime to bypass a static filter.

## Resolution method
1. **The mechanism (challenge.c)**

- `mmap` sets `0x123412340000`, **`PROT_READ|WRITE|EXEC`** (RWX), our code is read there (`read(0, resp,0x1000)`).
- `check()` scans the 0x1000 bytes and **rejects any `0f 05`** pair (syscall) in the **input** → `exit(-1)`.
- The check is **static and unique** (before execution). The buffer being modifiable at runtime, we can write the syscall there after the check.

2. **Method (self-modifying)**

1. Never put `0f 05` in the shipment. Place a **placeholder** `nop nop` where the syscall will go (label `trigger`).
2. At the beginning of the code: `lea rdi,[rip+trigger]` (placeholder address, position-independent); write `0x050f` on it.
   - **Trap**: the immediate `0x050f` itself contains the bytes `0f 05` → forbidden. We **make** it: `mov ax,0x0a1e; shr ax,1` → `ax=0x050f`, then `mov [rdi], ax`.
3. Prepare `execve("/bin/sh")` (`lea rdi,[rip+binsh]`, rsi=0, rdx=0, rax=59), then **fall into `trigger`** (become `syscall`).
4. `assert b"\x0f\x05" not in code` before sending (guaranteed to pass `check`). 44 bytes.

## Solve script
Script path: [scripts/solve.py](scripts/solve.py)

## Flag
sigpwny{code_is_data_is_code_is_data}

## Lessons and reusable patterns
- Code = data: an RWX buffer + a filter which only inspects the initial input = we write the prohibited instruction at execution.
- On x86, self-modifying code in the same thread is consistent (no need for cache flush): fall-through after writing executes the new instruction.
- Also think about the immediate: avoid the forbidden byte-pair even in the operands (here create 0x050f by arithmetic).
- Harder variant: wider filter (several patterns), W^X (no RWX -> mprotect would be needed, but mprotect itself = syscall...), or ASLR without known address (-> lea rip-relative remains the key).
- Flag: sigpwny{code_is_data_is_code_is_data} (not submitted). Script: work/solve.py.
