---
title: "PWN002"
ctf: "2026-battleCTF"
category: "pwn"
difficulty: "Not specified"
points: 72
techniques: ["xor-cipher", "rop", "seccomp", "stack-canary", "pie-bypass", "nx-bypass"]
tools: ["strings", "socat", "python"]
keywords: ["PWN002", "battleCTF", "pwn", "xor-cipher", "rop", "seccomp", "stack-canary", "pie-bypass", "nx-bypass", "strings", "socat", "python", "tcp", "xor", "libc", "canary"]
status: "solved"
has_script: true
source: "battleCTF/CHALLENGES/pwn/PWN002/notes.md"
---

# PWN002 (battleCTF, pwn)

## Summary
Challenge **PWN002** from the battleCTF CTF, pwn category. Main technique: xor-cipher. Pop rdi using a pext rdi, rax, rcx gadget, then open/read/write in raw syscalls.

## Statement and artefacts
Get a shell on the remote host and read the flag.

`main()` loops a menu function which does, per turn: read(*name*, 73) → `puts(buf)` [leak] → read(*message*, 256) [overflow] → `leave; ret`. `buf @ rbp-0x50`; canary @ off 72; saved_rbp @ 80; RIP @88.

- Exploit: `work/exp.py` (`--status` = diagnosis; `--local` = test, requires a dummy local `/flag/flag.txt`).

**Provided files / artifacts:**
- `work/ld-linux-x86-64.so.2 (file, 220.8 KB)`
- `work/libc.so.6 (file, 1.9 MB)`
- `work/vault (file, 14.1 KB)`
- `work/vault_patched (file, 20.0 KB)`

## Recognition signals
- Signal: ret2ORW on PIE binary + stripped + seccomp. Leak libc without.
- Signal: Full RELRO · NX · Canary · PIE · stripped · libc Debian glibc 2.42 (provided).
- If we observe ROP ORW of 256 B of a block = exact size of the server read, think of read() TCP renders.
- If we observe hardcoded fd (3): read(3,…) comes across a blocking fd, think of silent freezing.
- Signal: Diagnostic mode --status (ORW of /proc/self/status, which definitely exists) = key for.

## Resolution method
1. **Differences with PWN#001**

- **PIE** (randomized code) + **stripped**: a code address must first be leaked.
- **Reverse Seccomp**: BPF filter (5 instructions) ONLY kills `execve`(59)/`execveat`(322). `open`/`read`/`write` are **authorized** → we read a **file** (not an env var).
- The flag is a file: **`/flag/flag.txt`** (in the rest of the method).

2. **Operating chain**

1. **PIE leak (free)**: at startup `Vault seal: <pie+0x13a6>`. `pie = seal - 0x13a6`.
2. **Canary leak + saved_rbp**: read(name,73) in buf[72] + `\x01`(here `\x41`) overwrites the canary's `\x00` → `puts` spits it out. `canary = \x00 + 7 bytes`; saved_rbp follows.
3. **libc leak WITHOUT `pop rdi`** (binary has no argument gadget): gadget **`pext rdi, rax, rcx; ret`** (0x1529). With `rcx = 0xffffffffffffffff` (full mask), `pext` **copy `rax` into `rdi`** → synthetic `pop rdi` via `pop rax`(0x11e0) + `pop rcx`(0x1210) + `pext`. We call `puts@plt(&GOT[read])` → libc address of `read` → `libc.address = leak - read_off`. Back to the hand loop.
4. **ORW in raw syscalls** (movaps immune):
   - Turn A: `open("/flag/flag.txt", 0)` → fd in `rax`. **fd UNKNOWN in remote** (socat also opens fds → open returns 4+, not 3). We recover `rax → rdi` with the SAME gadget `pext`, then `read(fd, scratch, 0x100)` in the same turn.
   - Turn B: `write(1, scratch, 0x100)` (fd 1 known).
   - `scratch` = **`.bss` from libc** (`libc+0x1e8be0`, always mapped RW).

3. **Gadgets**

- Binary (PIE): `pop rax`=0x11e0, `pop rcx`=0x1210, **`pext rdi, rax, rcx`=0x1529**, `ret`=0x1016, `puts@plt`=0x1030, `GOT[read]`=0x3fb0, loop=0x148a, path=0x4070.
- libc 2.42: `pop rdi`=0x2a9b7, `pop rsi`=0x29e29, `pop rdx`=0x96372, `pop rax`=0x44386, `syscall;ret`=0x926e2.

4. **Protections**

Full RELRO · NX · Canary · **PIE** · stripped · libc Debian glibc 2.42 (provided).

5. **Remote (expensive) pitfalls and fixes**

- **ORW ROP of 256 B of a block = exact size of the server read** → `read()` TCP often renders less → truncated ROP → crash before `write`. **Fix: cut into several turns** (short ROP) and return to the hand loop between each (the fd remains open, living process).
- **hardcoded fd (`3`)**: `read(3,…)` came across an fd that **blocks** → silent freeze. **Fix: dynamic fd** (`rax`→`rdi` via `pext`), open+read merged in one round.
- Diagnostic mode `--status` (ORW of `/proc/self/status`, which definitely exists) = key to distinguishing “broken mechanics” from “bad flag path”.

## Solve script
Script path: [scripts/exp.py](scripts/exp.py)
Script path: [scripts/pwny.py](scripts/pwny.py)

## Flag
CTF{e0a79830f06dca87a52f8be6d895deae}

## Lessons and reusable patterns
- prctl in dynamic binary = seccomp. Decode the BPF filter on the stack: here it
- No rdi pop? Search for an exotic gadget: pext/pdep with full mask = move.
- In remote, never assume fd == 3: retrieve the fd rendered by open.
- Payload ≈ server read size = fragile: cut.
