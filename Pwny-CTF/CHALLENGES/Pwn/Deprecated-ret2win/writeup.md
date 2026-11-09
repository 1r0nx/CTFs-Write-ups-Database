---
title: "Deprecated-ret2win"
ctf: "Pwny-CTF"
category: "pwn"
difficulty: "Not specified"
points: 200
techniques: ["format-string", "buffer-overflow", "ret2win", "stack-canary", "pie-bypass", "nx-bypass"]
tools: ["gdb", "checksec", "netcat", "python"]
keywords: ["Deprecated-ret2win", "Pwny-CTF", "pwn", "format-string", "buffer-overflow", "ret2win", "stack-canary", "pie-bypass", "nx-bypass", "gdb", "checksec", "netcat", "python", "elf", "libc", "canary"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Pwn/Deprecated-ret2win/notes.md"
---

# Deprecated-ret2win (Pwny-CTF, pwn)

## Summary
Challenge **Deprecated-ret2win** from the Pwny-CTF CTF, pwn category. Main technique: format-string. Recognize: win/print_flag function never called + overflow (gets) + No PIE + No canary -> ret2win direct (overwrite the saved RIP).

## Statement and artefacts
Can you pwn this program? Look in challenge.c for hints!

`nc chal.sigpwny.com 1376`

**Provided files / artifacts:**
- `work/Dockerfile (file, 588 B)`
- `work/challenge (file, 19.3 KB)`
- `work/challenge_patched (file, 19.3 KB)`

## Recognition signals
- Signal: Offset saved RIP = buffer_size + 8 (saved RBP). cyclic + cyclic_find(crash_value) confirms this if necessary.
- Signal: If crash in print_flag/a libc (movaps) -> insert a ret gadget before to realign the stack on 16 bytes. Not necessary here.

## Resolution method
1. **Binary**

- `main()`: `char name[32];`, read by **`gets(name)`** (unbounded), then `printf("Nice to meet you, %s")`.
- `print_flag()` exists and displays `flag.txt`, but is **never called**.
- `checksec`: **Partial RELRO**, **No canary**, NX, **No PIE** (`0x400000`), unstripped. The source says it all: *"write the address of print_flag to the return address of main"*.

1. **No canary** → nothing between the buffer and the saved RIP to preserve: direct overflow.
2. **Offset = 40** up to return address: `32` bytes of `name` + `8` of saved RBP.
3. **PIE No** → `print_flag` is at a **fixed** address (`elf.sym["print_flag"]`, or `gdb`).
4. Payload = padding 40 + `p64(print_flag)`. At `ret` of `main`, execution jumps to `print_flag`.

```python
payload = cyclic(32) + b"B" * 8 + p64(elf.sym["print_flag"])
sla(b"?", payload)
```

## Solve script
Script path: [scripts/pwny.py](scripts/pwny.py)

## Flag
sigpwny{your_exploit_is_very_cool!}

## Lessons and reusable patterns
- Recognize: win/print_flag function never called + overflow (gets) + No PIE + No canary -> ret2win direct (overwrite the saved RIP).
- Offset saved RIP = buffer_size + 8 (saved RBP). cyclic + cyclic_find(crash_value) confirms this if necessary.
- No PIE = fixed and known address of print_flag (elf.sym/nm); with PIE it would first be necessary to leak the database (see 03/05).
- If crash in print_flag/a libc (movaps) -> insert a ret gadget before to realign the stack on 16 bytes. Not necessary here.
- Almost identical to 2 - Return and Bug Bounty 3.
