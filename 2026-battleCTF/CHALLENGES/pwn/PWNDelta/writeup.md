---
title: "PWNDelta"
ctf: "2026-battleCTF"
category: "pwn"
difficulty: "Not specified"
points: 148
techniques: ["format-string", "buffer-overflow", "rop", "stack-canary", "pie-bypass", "nx-bypass", "reverse-engineering", "malware-analysis"]
tools: ["radare2", "objdump", "socat", "python"]
keywords: ["PWNDelta", "battleCTF", "pwn", "format-string", "buffer-overflow", "rop", "stack-canary", "pie-bypass", "nx-bypass", "reverse-engineering", "malware-analysis", "radare2", "objdump", "socat", "python", "elf"]
status: "solved"
has_script: true
source: "battleCTF/CHALLENGES/pwn/PWNDelta/notes.md"
---

# PWNDelta (battleCTF, pwn)

## Summary
Challenge **PWNDelta** from the battleCTF CTF, pwn category. Main technique: format-string. Canary by overflowing its null MSB, then ROP chain to system("/bin/sh") while juggling the particular stack pivot of the PPC.

## Statement and artefacts
Get a shell on the remote host and read the flag.

- `ELF 32-bit MSB, PowerPC, statically linked, not stripped`. Partial RELRO, **Canary**, NX, **No PIE** (base 0x10000000).
- Host `objdump` does not know PPC → **radare2** with `-e cfg.bigendian=true -a ppc -b 32`.
- PPC convention: args in **r3..r10**, return in **r3**, return address in **LR** (not on stack), canary via TLS `lwz r9, -0x7008(r2)`. A function saves LR with `mflr`+`stw...,0x..(r1)` and restores it with `lwz`+`mtlr` in the epilogue.
- `vuln()` = state machine (variable at `0x18(r31)`), frame `0x70`, buffer at `0x1c(r31)`:
  - state 5: `read(0, buf, 0x41=65)`
  - state 6: `printf("Hello, %s\n", buf)` ← **leak**
  - state 8: `read(0, buf, 0x6c=108)` ← **overflow**
  - state 9: `puts("Message received.")` + **canary check** + epilogue (`mtlr` on saved LR, `blr`)

**Provided files / artifacts:**
- `work/vault (file, 702.1 KB)`

## Recognition signals
- Signal: ROP on PowerPC 32-bit big-endian, static + No PIE + canary. Leak from.
- Signal: Pivot via prologue: a stwu r1, -X(r1) in a gadget is a free stack pivot when r1.
- Signal: socat ⇒ partial read: provide a retry if the final state is not reached.

## Resolution method
1. **Offsets (from buf)**

| offset | role |
|--------|------|
| 64 (0x5c) | rescued canary |
| 76 (0x68) | r30 saved |
| 80 (0x6c) | r31 saved |
| 84 (0x70) | back-chain → **r1 after the epilogue** |
| 88 (0x74) | **LR saved** (1st controlled jump) |

Epilogue: `r1 = r31+0x70 = buf+84`, LR read to `buf+88`.

2. **🔑 Step 1 — canary leak (zero MSB overflow)**

The big-endian PPC canary is stored `00 c1 c2 c3`: its **1st (most significant) byte is zero**. A `printf("%s")` stops on this zero → impossible to read it as is. The 65-byte `read` (state 5) writes **exactly 1 byte too many**: offset 64 = the MSB of the canary. We send `"A"*64 + "\xff"`: `\xff` overwrites the zero, `%s` continues and leaks the 3 low bytes. We reconstruct: `canary = b"\x00" + leak[1:4]`.

3. **🔑 Step 2 — ROP to system("/bin/sh")**

After the epilogue: we control LR (offset 88) but **r1 = buf+84**, so there are only 24 bytes of “ROP stack” left (the limit of `read` is 108) → not enough, and a clean pop-r3 would read its LR out of zone. **Pivot Tip**: Gadget functions are planted in the binary. `gadget_load_r9` (`0x100007cc`) starts with `stwu r1, -0x30(r1)` which **brings r1 from buf+84 to buf+36** (we recover ~72 B), then its tail does `lwz r0,4(r1); mtlr r0; addi r1, r1,8; blr` → pop of the next LR and chaining.

Final string:
1. `LR@88 = gadget_load_r9` → r1 pivots to buf+36, next LR = `[buf+40]`, r1 = buf+44.
2. `[buf+40] = pop_r3` (`0x1006c9b4`: `lwz r3,0x10(r1); lwz r0,0x24(r1); lwz r30,0x18(r1); addi r1, r1,0x20; mtlr r0; blr`) → at r1=buf+44: **r3 = [buf+60]**, **LR = [buf+80]**.
3. `[buf+60] = 0x10074850` (&"/bin/sh"); `[buf+80] = 0x100020d0` (`system`) → **shell**.

Canary at offset 64 returned identically (checked at state 9 before the epilogue).

The remote service is behind **socat** → its `read()` on pipe can return a **partial read**: if the 108 bytes do not arrive in one block, the canary is not rewritten → `__stack_chk_fail`. The solve retries until you see “Message received. ". Flag in env variable `FLAG` (and `/flag/flag.txt`).

## Solve script
Script path: `scripts/solve.py`

## Flag
CTF{c9a9816576849a4aae690a65c1fba37d}

## Lessons and reusable patterns
- PPC = LR, not the stack: we do not overwrite the “return address on the stack” but the saved LR slot
- Big-endian canary: null MSB -> overflowing it by 1 byte transforms a simple overflow into a leak.
- Pivot via prologue: a stwu r1, -X(r1) in a gadget is a free stack pivot when r1
- radare2 to disassemble the PPC; qemu-ppc-static (+ chmod +x on copy) to test locally
- socat ⇒ partial read: provide a retry if the final state is not reached.
- Script: work/solve.py.
