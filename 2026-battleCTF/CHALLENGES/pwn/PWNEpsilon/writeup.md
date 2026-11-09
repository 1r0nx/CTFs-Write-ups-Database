---
title: "PWNEpsilon"
ctf: "2026-battleCTF"
category: "pwn"
difficulty: "Not specified"
points: 74
techniques: ["xor-cipher", "format-string", "buffer-overflow", "rop", "seccomp", "stack-canary", "pie-bypass", "reverse-engineering"]
tools: ["radare2", "objdump", "checksec", "ropper", "ropgadget", "capstone", "python"]
keywords: ["PWNEpsilon", "battleCTF", "pwn", "xor-cipher", "format-string", "buffer-overflow", "rop", "seccomp", "stack-canary", "pie-bypass", "reverse-engineering", "radare2", "objdump", "checksec", "ropper", "ropgadget"]
status: "solved"
has_script: true
source: "battleCTF/CHALLENGES/pwn/PWNEpsilon/work/notes.md"
---

# PWNEpsilon (battleCTF, pwn)

## Summary
Challenge **PWNEpsilon** from the battleCTF CTF, pwn category. Main technique: xor-cipher. The binary has a canary (failed by checksec) and system() is unusable (seccomp blocks fork/clone), so we start with a direct execve by syscall (a7=221, ecall).

## Statement and artefacts
Get a shell on the remote host and read the flag.

- `ELF 64-bit RISC-V, RVC double-float, statically linked, No PIE (base 0x10000), stripped`.
- Same “state machine” program as Delta/Alpha/Beta: `Enter your name:` (read 65) → `Hello,%s` (leak) → `Leave a message...` (read **200** = overflow) → `Message received.` → check canary → ret.
- objdump does not decode RISC-V here → **radare2** (`pd`, `aaa`). ROPgadget/ropper do not support RISC-V → **capstone home gadget finder** (`work/rvgadget.py`).
- qemu-riscv64 local **unusable** (binary loaded at 0x10000 < `mmap_min_addr`=0x10000, qemu lease; lower sysctl refused). Adjusted by **remote diagnosis** (in the rest of the method).

**Provided files / artifacts:**
- `work/vault (file, 451.8 KB)`

## Recognition signals
- Signal: ROP on static RISC-V 64 (No PIE, canary) to execve("/bin/sh",0,0).
- If we observe checksec “No canary” false negative on static RISC-V, remember to always check in disassembly.
- If we observe system() silent = most likely seccomp (fork/clone blocked), consider switching to execve syscall.
- Signal: Rare “call with a0” gadget; we route via s0 controlled + mv a0, s0 (gadget 0x18574) which poses.
- If we observe sd aX, off(aY) in a gadget, consider aiming for a writable page outside RELRO, otherwise SIGSEGV.
- Signal: RISC-V ret = c.jr ra at capstone 6 (not c.ret); execve = a7=221, /bin/sh @ 0x52ab8.

## Resolution method
1. **vuln() @ 0x10608 — offsets from buf**

| offset | role |
|--------|------|
| 0..63  | buffer (read name 65 B, read message 200 B) |
| 64     | canary (8 B) |
| 72     | s0 saved |
| 80     | r saved ← 1st controlled jump |
Epilogue: `ld ra,88(sp); ld s0,80(sp); addi sp,96; ret` → **string entry: sp = buf+88**.

2. **Escape from the canary**

The read of *name* reads **65** bytes in `buf` → byte 64 overwrites the **null LSB** of the canary. `printf("Hello, %s")` then dump `buf` until the next `\0` → we recover `canary[1..7]`. `canary = b"\x00" + leak7`. We put it back as is in the overflow (otherwise `__stack_chk_fail`).

3. **ROP chain (execve) — 4 steps, holds 184 B**

RISC-V does not have an “a0/a1/a2 pop”. We exploit the fact that we **control s0** (restored from buf+72) and we chain gadgets that load from the stack:
1. `s0 = &"/bin/sh"` (0x52ab8) via slot s0 saved (buf+72) — **preserved** by the following 2 gadgets.
2. **g_a7 @ 0x1475e**: `a6=[sp+8]; a7=[sp+0x10]=221; ra=[sp+0x38]; sd a0,0x20(a6); a0=a7; sp+=0x40` → `a7=221`. ⚠ `a6` must aim for **writable excluding RELRO** (RELRO = 0x7b698..0x7f000; we take 0x80000).
3. **g_a5 @ 0x15820**: `a5=[sp+8]=0x102dc(ecall); ra=[sp+0x18]; (clobbe a0); sp+=0x20`.
4. **end @0x18574**: `li a2,0; li a1,0; mv a0, s0; jalr a5` → `execve("/bin/sh",0,0)` with `a7=221`. 🐚

Payload offsets (from buf): 64=canary, 72=binsh, 80=g_a7, 96=0x80000(a6), 104=221(a7), 144=g_a5 (ra of g_a7), 160=ecall (a5 of g_a5), 176=end (ra of g_a5).

4. **Remote debug method (without qemu) — reusable**

To validate a RISC-V chain blindly: **replace the final target with `vuln` (0x10608)**. If the service **re-displays “Enter your name:”**, the chain executes and the registers are good; only the final syscall/function remains. This is what made it possible to isolate: (a) canary OK, (b) `a0=/bin/sh` delivered, (c) `system` fails = seccomp, (d) an **offset bug** (g_a7 makes `sp+=64` → output buf+152, not buf+128).

5. **To remember / pitfalls**

- **checksec “No canary” false negative** on static RISC-V → always check in disassembly (`__stack_chk_fail` @ 0x21220, xor against a global guard).
- `system()` mute = most likely **seccomp** (fork/clone blocked) → move to **execve syscall**.
- Rare “call with a0” gadget; we route via **s0 controlled** + `mv a0, s0` (0x18574 gadget) which also poses `a1=a2=0`: ideal for execve.
- `sd aX, off(aY)` in a gadget → aim for a page **writable outside RELRO**, otherwise SIGSEGV.
- RISC-V `ret` = `c.jr ra` at capstone 6 (not `c.ret`); execve = **a7=221**, `/bin/sh` @ 0x52ab8.
- Script: `work/solve.py` (`--remote`). Tools: `work/rvgadget.py` (RISC-V capstone finder).

## Solve script
Script path: [scripts/rvgadget.py](scripts/rvgadget.py)
Script path: [scripts/solve.py](scripts/solve.py)

## Flag
CTF{d45cfcb9f43f7d1a28b2f678b0b5c72f}

## Lessons and reusable patterns
- Main technique: xor-cipher.
- ROP on static RISC-V 64 (No PIE, canary) to execve("/bin/sh",0,0).
