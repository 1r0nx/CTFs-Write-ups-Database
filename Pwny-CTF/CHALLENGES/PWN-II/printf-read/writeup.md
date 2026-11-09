---
title: "printf-read"
ctf: "Pwny-CTF"
category: "pwn"
difficulty: "Not specified"
points: 150
techniques: ["format-string", "stack-canary", "pie-bypass", "nx-bypass"]
tools: ["checksec", "netcat", "python"]
keywords: ["printf-read", "Pwny-CTF", "pwn", "format-string", "stack-canary", "pie-bypass", "nx-bypass", "checksec", "netcat", "python", "canary", "aslr", "pie", "stack"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/PWN-II/printf-read/notes.md"
---

# printf-read (Pwny-CTF, pwn)

## Summary
Challenge **printf-read** from the Pwny-CTF CTF, pwn category. Main technique: format-string. %s vs %p/%lx: %p reads the raw value of the slot (good when the secret IS on the stack, cf. 00 - Stack Read); %s dereferences this slot as an address and reads the pointed string (good when the slot is a pointer to the secret, like here).

## Statement and artefacts
Can you read the flag? It is important to note that in this C program, `flag`'s pointer is on the stack, but its characters are not. (This is unlike our stack buffers we are used to, where all the characters are on the stack)

`nc chal.sigpwny.com 1371`

**Author**: Nathan

**Provided files / artifacts:**
- `work/Dockerfile (file, 394 B)`
- `work/challenge (file, 19.6 KB)`
- `work/challenge_patched (file, 19.6 KB)`

## Recognition signals
- Signal: "flag's pointer is on the stack, but its characters are not" + hints: "uses %s" and "direct parameter access".
- Signal: %p / %lx at the flag offset would display the heap address, not the text. It takes %s to follow the pointer to the characters.
- Signal: %s vs %p/%lx: %p reads the raw value of the slot (good when the secret IS on the stack, cf. 00 - Stack Read); %s dereferences this slot as an address and reads the pointed string (good when the slot is a pointer to the secret, like here).
- Signal: Pitfall: targeting the flag with %p here would only give a useless heap address. The title/subscripts ("characters are not on the stack", "use %s") point exactly to the dereference.

## Resolution method
1. **The program (challenge.c)**

- `read_flag()`: `calloc(0x100)` on the **heap**, copies `flag.txt` there, returns the pointer.
- `main()`: `char *flag = read_flag();` → the **pointer** lives on the stack, the **bytes** of the flag live on the heap.
- Bug: `printf(name);` → our entry serves as **format string** (classic format string).
- `checksec`: Full RELRO, Canary, NX, PIE. But here **no protection is in the way**: we only *read*, not overwrite.

1. Confirmed format string bug: `printf(name)` without `%s`.
2. **Direct parameter access** `%N$s`: instead of `%s %s %s...`, we directly target the Nth argument.
3. **Scan N** until you come across the slot which contains the pointer `flag` → `offset_browser(fmt="s", reconnect=True)` reconnects and tests `%1$s`, `%2$s`, …
4. Low reads (`%1$s`, `%2$s`) → string echo or `(null)`/crash (slots that are not valid pointers). **Offset 7** (`%7$s`) → the `flag` pointer is dereferenced → **flag**.

```python
# pwny.py
offset_browser(fmt="s", prompt=b"?\n", reconnect=True)
# is equivalent to sending "%1$s", "%2$s",... and reading the output; offset 7 gives the flag
# minimal payload once the offset is known:
# sl(b"%7$s")
```

2. **Subtlety (platform clues)**

- *"flag's pointer is on the stack, but its characters are not"* + hints: **“uses `%s`”** and **“direct parameter access”**.
- `%p` / `%lx` at the flag offset would display the **heap address**, not the text. It takes `%s` to **follow** the pointer to the characters.

## Solve script
Script path: [scripts/pwny.py](scripts/pwny.py)

## Flag
sigpwny{reading_down_the_stack}

## Lessons and reusable patterns
- %s vs %p/%lx: %p reads the raw value of the slot (good when the secret IS on the stack, cf. 00 - Stack Read); %s dereferences this slot as an address and reads the pointed string (good when the slot is a pointer to the secret, like here).
- Direct parameter access %N$s: direct access to the Nth argument, essential to target a specific slot without aligning dozens of %s.
- Reconnection on each test: with PIE/ASLR the offset (distance in slots) remains constant from one run to another, so brute-forcing N by reconnecting works. A %s on a non-pointer slot can crash (EOF) or display (null) -> we continue.
- Pitfall: targeting the flag with %p here would only give a useless heap address. The title/subscripts ("characters are not on the stack", "use %s") point exactly to the dereference.
- Differs from 01 - Arbitrary Read: here we placed the target address in the buffer then %N$s; here the address (the flag pointer) is already on the stack, we just read it at the right offset.
