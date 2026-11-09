---
title: "Project-Mangoo"
ctf: "2026-hiCTF"
category: "pwn"
difficulty: "Not specified"
points: null
techniques: ["rop", "stack-canary", "pie-bypass", "nx-bypass", "git-forensics", "encoding", "wifi"]
tools: ["socat", "python"]
keywords: ["Project-Mangoo", "hiCTF", "pwn", "rop", "stack-canary", "pie-bypass", "nx-bypass", "git-forensics", "encoding", "wifi", "socat", "python", "pe", "hex", "canary", "aslr"]
status: "solved"
has_script: true
source: "hiCTF/pwn/Project-Mangoo/notes.md"
---

# Project-Mangoo (hiCTF, pwn)

## Summary
Challenge **Project-Mangoo** from the hiCTF CTF, pwn category. Main technique: rop. The Project-Mangoo challenge (hiCTF, pwn) is documented by a resolution note.

## Statement and artefacts
**Provided files / artifacts:**
- `project-mangoo.zip (archive, 65.6 KB)`

## Recognition signals
- Signal: Query (leak) shows ID=dword[rsi+i*0x20+0x60], Status=+0x64, Label=qword+0x68, Ref=qword+0x70.
- If we look at Query -3, think of Ref = qword[rsi+0x10] = 0x140001550 ⇒ base image (base = Ref - 0x1550).
- Signal: Query -1 -> Ref = qword[rsi+0x50] ⇒ address of the flag (strncpy buffer of the env, 0x7f0000).
- If we observe Query 0, think of Ref = qword[rsi+0x70] ⇒ address of the arena (0x7e0000, see below).
- Signal: Sync (call primitive) with i=-2.
- Signal: Trap 1 — buffered output: stdout passes through a socat pipe ⇒ _IOFBF. puts(flag) NEVER leaves without an explicit fflush, and exit() under wine crashes before flushing -> always fflush(NULL) in the string.

## Resolution method
1. **Protocol (“GATEWAY” console)**

1. Handshake: the server sends `Session Challenge: <64 hex>` (32 B) and waits for a `Authorization Token`. Algo found: for i∈[0,32), `token[i] = rol8(ch[i],3) ^ (0x11*i & 0xFF) ^ 0x6a`, sent in hex.
2. Menu: `1` Ingest (Size≤0x2c00 + Stream to `%02x`), `2` Query (reads a “channel”), `3` Commit, `4` Status, `5` Terminate, `6` Sync.

2. **Operating chain (ROP, “deep” pivot)**

Ingest writes our bytes into the arena; `Sync -2` makes `call qword[arena+0x10]`.

1. **Pivot** `mov rax,[rcx]; mov rsp, rax; add rsp,0x18; ret` (`base+0x16d0`): `rcx=rsi+0x18` → `rsp = arena+0x18`.
2. **`pop rsp; ret`** (`base+0x169f`) → `rsp = arena+0x2000` (**middle** of the arena; see trap 2).
3. `pop rcx; ret` (`base+0xbd60`) → `rcx = flag`; `jmp [puts]` (`base+0x18348`) → **`puts(flag)`**.
4. `add rsp,0x28; ret` (`base+0x14e8`) to **skip the ghost space** of `puts`, then `rcx=0` and `jmp [fflush]` (`base+0x183d8`) → **`fflush(NULL)`** (essential, see trap 1), then `jmp [exit]` (`base+0x183e0`).

Complete and commented script: `work/solve.py` (auth + 3 leaks + payload + trigger).

3. **The 2 bugs (negative channel index)**

Context `rsi`. An index channel `i` is read at `rsi + i*0x20`; **only terminal `i>15` is checked** → `i` **negative** = reading/use **outside terminal** under context.

- **Query (leak)** displays `ID=dword[rsi+i*0x20+0x60]`, `Status=+0x64`, `Label=qword+0x68`, `Ref=qword+0x70`.
  - `Query -3` → `Ref = qword[rsi+0x10] = 0x140001550` ⇒ **base image** (`base = Ref - 0x1550`).
  - `Query -1` → `Ref = qword[rsi+0x50]` ⇒ **flag address** (env buffer `strncpy`, `0x7f0000`).
  - `Query 0` → `Ref = qword[rsi+0x70]` ⇒ **address of the arena** (`0x7e0000`, see below).
- **Sync (call primitive)** with `i=-2`:
  ```
  arena = qword[rsi+0x18]; buffer that Ingest fills
  rdx = qword[arena+0x10]; 8 bytes 100% controlled
  if rdx != cookie[rsp+0x28]: call rdx ; INDIRECT CALL controlled
  ```
At the time of `call`, `rcx = rsi+0x18` (**not** the flag) → impossible to call `puts(flag)` directly.

4. **Traps / to remember (what cost the flag)**

- **Trap 1 — buffered output**: `stdout` passes through a pipe `socat` ⇒ `_IOFBF`. `puts(flag)` NEVER leaves without an explicit `fflush`, and `exit()` under wine crashes before dumping → **always `fflush(NULL)`** in the chain.
- **Trap 2 — pivot too low = SEGV**: the pivot places `rsp = arena+0x18`, at the very bottom** of the `0x4000` o of the arena. As soon as `puts` stacks, `rsp` goes **under** the (unmapped) arena → segfault. We need a **2ᵉ pivot** (`pop rsp`) which places `rsp` **in the middle** of the arena to leave room for `push`. ⇒ “pivot deeper”.
- **Windows x64 ABI**: 1st arg in **`rcx`** (not `rdi`); each function has **0x20 where shadow space** can be clobbered above its return address → jump via `add rsp,0x28`. Function input aligned to **8 mod 16**.
- **No ASLR** (PE base `0x140000000`, effective non-PIC image) ⇒ gadgets and import stubs (`jmp [iat]`) with **absolute** addresses.
- **Recognize**: service `.exe` under wine + `socat`, menu with poorly bounded signed index (`cmp ax,0xf; jg` without lower bound) → negative OOB = leaks + call primitive.

## Solve script
Script path: [scripts/diag.py](scripts/diag.py)
Script path: [scripts/diag2.py](scripts/diag2.py)
Script path: [scripts/exploit.py](scripts/exploit.py)
Script path: [scripts/mangoo.py](scripts/mangoo.py)
Script path: [scripts/solve.py](scripts/solve.py)

## Flag
hiCTF{n0_g4dg3ts_n0_sh3llc0d3_jusT_p1v0t_d33p3r_1f18a650c4}

## Lessons and reusable patterns
- Main technique: rop.
