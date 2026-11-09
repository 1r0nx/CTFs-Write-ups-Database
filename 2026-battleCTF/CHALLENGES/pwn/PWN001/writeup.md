---
title: "PWN001"
ctf: "2026-battleCTF"
category: "pwn"
difficulty: "Not specified"
points: 45
techniques: ["buffer-overflow", "rop", "seccomp", "stack-canary", "pie-bypass", "nx-bypass"]
tools: ["pwntools", "checksec", "socat", "python"]
keywords: ["PWN001", "battleCTF", "pwn", "buffer-overflow", "rop", "seccomp", "stack-canary", "pie-bypass", "nx-bypass", "pwntools", "checksec", "socat", "python", "libc", "canary", "pie"]
status: "solved"
has_script: true
source: "battleCTF/CHALLENGES/pwn/PWN001/notes.md"
---

# PWN001 (battleCTF, pwn)

## Summary
Challenge **PWN001** from the battleCTF CTF, pwn category. Main technique: buffer-overflow. Arbitrary memory reading by write(1, addr, n) when execve/open are blocked by seccomp. The flag is not a file, it is an environment variable on the stack.

## Statement and artefacts
Get a shell on the remote host and read the flag.

- Final exploit: `work/exp.py` (remote by default; `--local` for testing).
- Context leaks confirmed: `PWD=/challenge`, `SOCAT_*` (service exposed via socat).

**Provided files / artifacts:**
- `work/ld-linux-x86-64.so.2 (file, 220.8 KB)`
- `work/libc.so.6 (file, 1.9 MB)`
- `work/vault (file, 15.7 KB)`
- `work/vault_patched (file, 23.7 KB)`

## Recognition signals
- Signal: arbitrary memory reading by write(1, addr, n) when execve/open are blocked by seccomp. The flag is not a file, it is an environment variable on the stack.
- Signal: The statement says "Get a shell": decoy.
- Signal: A seccomp blocks execve AND open/openat (SIGSYS if they are called).
- Signal: Only read/write/getpid passes.
- Signal: So no shell, no file to open: we read the flag directly from memory.
- Signal: No PIE -> the binary has a fixed address,.bss (0x404800) usable as a buffer.

## Resolution method
1. **The 3 leaks (all via read1's puts, which stops at the first \x00)**

1. **libc, without ROP**: on the first pass, the setup leaves `&_IO_2_1_stdout_` at `buf+0x08` (= `libc_base + 0x1e85c0`). Send **8 bytes** → `puts` spits out this pointer. `libc.address = leak - 0x1e85c0`. Guardrail: `libc.address & 0xfff == 0`.
2. **canary**: the canary ends with `\x00`. Send **72 B + `\x01`** overwrites this terminal `\x00` → `puts` spits out the next 7 bytes. `canary = \x00 + 7_bytes`.
3. **saved_rbp**: just after the canary in the same leaked line (6 bytes). Check: `(saved_rbp >> 40) == 0x7f`.

2. **Golden rule: RAW SYSCALLS only**

Call a libc **function** by ROP (`system`, `puts`, `rop.execve`) **crash in remote**: the `movaps` instruction requires an aligned stack 16 (a real aligned `call`, not our ROP). → only use the `syscall; ret` gadget (no movaps). Trap encountered: `libc.sym['syscall']` = the **C function** (number in RDI) → SIGSEGV; take the raw instruction via `next(libc.search(asm("syscall; ret")))`.

ROP chain (memory read + keep-alive):
```
pop rax=1; pop rdi=1; pop rsi=ADDR; pop rdx=N; syscall   # write(1, ADDR, N)
pop rax=0; pop rdi=0; pop rsi=BSS;  pop rdx=1; syscall   # read(0, BSS, 1) -> keeps the process alive
```
The blocking `read` prevents the process from crashing just after the `write` (reliable output).

3. **libc 2.42 gadgets (raw offsets, to be rebased)**

`pop rdi=0x2a9b7` · `pop rsi=0x29e29` · `pop rdx=0x96372` · `pop rax=0x44386` `syscall;ret` via `libc.search`. `_IO_2_1_stdout_ = 0x1e85c0`. pwntools trap: after `libc.address = X`, `libc.sym[name]` returns **absolute** addresses (base included) → never redo `+ base`. Capture offsets BEFORE rebasing.

4. **The trap**

The statement says *"Get a shell"*: decoy. A **seccomp** blocks `execve` AND `open`/`openat` (SIGSYS if called). Only `read`/`write`/`getpid` pass. So no shell, no file to open: we read the flag directly from memory.

5. **Protections (checksec)**

Full RELRO · NX · **Canary** · **No PIE** · libc Debian glibc 2.42 (provided).
- No PIE → the binary has a fixed address, `.bss` (`0x404800`) usable as a buffer.
- Canary → you have to leak it to overflow without crashing.

6. **The flaw**

`vuln()`: `char buf[72]` to `rbp-0x50`. Offsets from the start of the buffer: canary = 72, saved_rbp = 80, RIP = 88. Two readings: read1 (73 B) then `puts(buf)` = **leak**; read2 (256 B) = **overflow**. `main()` **infinite loop** on `vuln()` → we return to the beginning as many times as we want in the same connection (essential to chain leaks then ROP).

7. **To remember (recognize this type)**

- Statement "get a shell" + **libc provided** + it crashes on `execve` remotely → think **seccomp** (check `open`/`openat` too). If blocked: flag in memory (often env var), not a file.
- Infinite loop on the vulnerable function = we can leak THEN exploit without doing everything at once.
- ROP crash remotely but OK locally on a `call` of libc function = **movaps alignment** → switch to raw syscalls.
- Env at random offset = sweep sizes from `saved_rbp`, not store a delta.

## Discarded approaches
- The env strings are above saved_rbp.
- The kernel randomizes the top of the stack: delta_str = (env string address) - saved_rbp changes on each connection (see 0x6ab, 0xd2b…).
- Cannot reuse an offset from one connection to another.
- On the other hand, saved_rbp is constant in a connection, and we re-leak it each time.
- Winning strategy (exp.py): at each connection, write(1, saved_rbp, size) of a **large block**, scanning the sizes 0x1400 -> 0x900 over several passes.
- A connection eventually falls on a compatible gap (delta_str ≤ size ≤ stack_top - saved_rbp) -> the block contains the string area of env, so FLAG=CTF{...}.
- (Fallen after ~13 logins.)
- Note on EFAULT: if size crosses the guard page, write returns 0 (empty output) -> we reduce the size (this is the role of decreasing scanning).

## Solve script
Script path: [scripts/exp.py](scripts/exp.py)
Script path: [scripts/exploit.py](scripts/exploit.py)
Script path: [scripts/pwny.py](scripts/pwny.py)

## Flag
CTF{ee6c8e12d8a68dcd220ebe010e2cfa4b}

## Lessons and reusable patterns
- Main technique: buffer-overflow.
- arbitrary memory reading by write(1, addr, n) when execve/open are blocked by seccomp. The flag is not a file, it is an environment variable on the stack.
