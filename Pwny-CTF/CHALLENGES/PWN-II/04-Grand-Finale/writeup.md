---
title: "04-Grand-Finale"
ctf: "Pwny-CTF"
category: "pwn"
difficulty: "Not specified"
points: 400
techniques: ["format-string", "got-overwrite", "stack-canary", "pie-bypass", "nx-bypass"]
tools: ["checksec", "netcat", "python"]
keywords: ["04-Grand-Finale", "Pwny-CTF", "pwn", "format-string", "got-overwrite", "stack-canary", "pie-bypass", "nx-bypass", "checksec", "netcat", "python", "elf", "canary", "pie", "got"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/PWN-II/04-Grand-Finale/notes.md"
---

# 04-Grand-Finale (Pwny-CTF, pwn)

## Summary
Challenge **04-Grand-Finale** from the Pwny-CTF CTF, pwn category. Main technique: format-string. Recognize: printf(user) + Partial RELRO + No PIE + a win/print_flag function never called -> GOT overwrite from a re-called function to the winning function.

## Statement and artefacts
This challenge requires an arbitrary write to the GOT. Reference the slides!

```nc chal.sigpwny.com 1385```

**Author**: Kevin Higgs

**Provided files / artifacts:**
- `work/grand_finale (file, 16.9 KB)`
- `work/grand_finale_patched (file, 16.9 KB)`

## Recognition signals
Not specified.

## Resolution method
1. **Binary**

- Vuln: `greet()` does `printf(name)` → **format string**, in an **infinite `while(1)` loop**.
- `checksec`: **Partial RELRO**, **Canary**, NX, **No PIE** (`0x400000`), unstripped.
- `print_flag()` exists and reads `flag.txt`, but is **never called**.
- Reading the protections:
  - **Partial RELRO** = the GOT remains **writable** (unlike 03 in Full RELRO) → you can write on it.
  - **No PIE** = `elf.sym["print_flag"]` (`0x40129b`) and `elf.got["printf"]` (`0x404030`) are **fixed**, known in advance.
  - **Canary** present **but out of play**: the exploit writes directly to the GOT via `%n`, without overflowing the stack or touching the return address → the canary is never checked against us.

1. **Find the offset** of the format string (`offset_browser`, or spray `%p.`×20) → `OFFSET = 10` (index where our entry begins).
2. **Overwrite `printf@GOT`** with the address of `print_flag`:
   ```python
   payload = fmtstr_payload(OFFSET, {elf.got["printf"]: elf.sym["print_flag"]}, write_size="byte")
   sla(b"? ", payload)
   ```
   - `fmtstr_payload` automatically generates the necessary `%n`/`%hhn`. `write_size="byte"` = write **byte by byte** (`%hhn`) → short payload, no gigantic field width.
3. **Detonator = the infinite loop**: just after writing, the next `printf(...)` in the program (`"What is your name? "`, then `"Hello "`) actually jumps to `print_flag()` → the flag is read and displayed (in a loop).

Launch: `./pwny.py --remote --host chal.sigpwny.com --port 1385`.

## Solve script
Script path: [`scripts/pwny.py`](scripts/pwny.py)

## Flag
sigpwny{you_are_a_format_string_g0d}

## Lessons and reusable patterns
- Recognize: printf(user) + Partial RELRO + No PIE + a win/print_flag function never called -> GOT overwrite from a re-called function to the winning function.
- Which GOT entry to aim for: a function called after we write it. Here printf is recalled at each loop turn -> ideal target. (Aiming for exit/a function never called back would not trigger anything.)
- Canary ≠ obstacle here: it only protects the return address on the stack. A %n towards the GOT does not go through there -> no need to leak/rewrite it.
- Partial vs Full RELRO: Full RELRO (see 03) remaps the GOT as read-only -> this write would be impossible, we fall back on a read (arbitrary read). Partial RELRO leaves the GOT open.
- Let fmtstr_payload do the %n calculations (byte order, cumulative widths): doing it by hand is painful and error-prone. write_size="byte" by default to keep it short.
