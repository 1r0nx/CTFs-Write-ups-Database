---
title: "03-Leak-and-Read"
ctf: "Pwny-CTF"
category: "pwn"
difficulty: "Not specified"
points: 300
techniques: ["format-string", "stack-canary", "pie-bypass", "nx-bypass"]
tools: ["gdb", "checksec", "netcat", "python"]
keywords: ["03-Leak-and-Read", "Pwny-CTF", "pwn", "format-string", "stack-canary", "pie-bypass", "nx-bypass", "gdb", "checksec", "netcat", "python", "elf", "canary", "pie", "got", "padding"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/PWN-II/03-Leak-and-Read/notes.md"
---

# 03-Leak-and-Read (Pwny-CTF, pwn)

## Summary
Challenge **03-Leak-and-Read** from the Pwny-CTF CTF, pwn category. Main technique: format-string. Recognize: printf(user) + global flag + PIE -> no GOT (Full RELRO) -> leak code scheme then arbitrary read. This is the PIE variant of 01 - Arbitrary Read (where, in No PIE, &flag = elf.sym["flag"] directly).

## Statement and artefacts
This challenge requires a PIE leak, followed by an arbitrary read. Reference the slides!

```nc chal.sigpwny.com 1383```

**Author**: Kevin Higgs

**Provided files / artifacts:**
- `work/leak_and_read (file, 16.9 KB)`
- `work/leak_and_read_patched (file, 16.9 KB)`

## Recognition signals
- Signal: Trap: leak_hex_int(., with_prefix=True) only keeps 0x of at least 4 digits -> the index to use counts after elimination of (nil)/small values.

## Resolution method
1. **Binary**

- Vuln: `greet()` does `printf(name)` (user input as format string) → **format string**.
- `checksec`: **Full RELRO**, **No canary**, NX, **PIE**. The flag is a **global** `char flag[32]`, filled from `flag.txt` at startup (therefore in memory, in the binary image).
- Consequences: Full RELRO = no overwriting of GOT; PIE = the address of `flag` changes with each run → you must first **leak** the base of the binary. The flag is not on the stack → `%s` alone does not cross it, it requires a **read at chosen address**.

2. **Method (2 steps, single connection)**

1. **PIE leak** — send `%p.`×15 as name → `printf` spits 15 values from the stack.
   - Among them, a **pointer in the binary code** (here `0x5eae96f163bf`, a return address to `main`). It is `leak_hex_int(res, True)[4]` (5ᵉ prefixed value `0x` of at least 4 digits; `(nil)` and `0x6` are ignored).
   - `flag_addr = ptr_code + 0x2CA1`. The offset `0x2CA1` = `&flag - ptr_code`, **constant under PIE** (code and global move together). It is measured once locally under GDB (`p &flag` minus the leaked address).
2. **Arbitrary reading** — `payload = b"%11$s" + b"ABC" + p64(flag_addr)`.
   - `p64(flag_addr)` is placed in the buffer `name`; `%11$s` dereferences argument #11, which falls right on this `p64`. The 3 bytes `"ABC"` **padding** aligns the address over 8 bytes so that it lands exactly in slot 11.
   - `printf` displays the pointed string → `Hello sigpwny{i_love_pie}`.

Launch: `./pwny.py --remote --host chal.sigpwny.com --port 1383`.

## Solve script
Script path: `scripts/pwny.py`
Script path: `scripts/solve.template.py`

## Flag
sigpwny{i_love_pie}

## Lessons and reusable patterns
- Recognize: printf(user) + global flag + PIE -> no GOT (Full RELRO) -> leak code scheme then arbitrary read. This is the PIE variant of 01 - Arbitrary Read (where, in No PIE, &flag = elf.sym["flag"] directly).
- The central tip: under PIE we do not know any absolute address, but the internal distances in the binary are fixed -> leak any pointer from the binary is enough, we add the constant offset towards the target.
- %N$s reads at an address provided in the buffer: find N (here 11) and pad to align p64 on the correct slot (8 bytes). Check N/alignment with offset_browser + local trial and error.
- Trap: leak_hex_int(..., with_prefix=True) only keeps 0x of at least 4 digits -> the index to use counts after elimination of (nil)/small values.
