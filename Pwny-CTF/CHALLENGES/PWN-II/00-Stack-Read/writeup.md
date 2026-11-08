---
title: "00-Stack-Read"
ctf: "Pwny-CTF"
category: "pwn"
difficulty: "Not specified"
points: 150
techniques: ["format-string"]
tools: ["netcat", "python"]
keywords: ["00-Stack-Read", "Pwny-CTF", "pwn", "format-string", "netcat", "python", "stack"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/PWN-II/00-Stack-Read/notes.md"
---

# 00-Stack-Read (Pwny-CTF, pwn)

## Summary
Challenge **00-Stack-Read** from the Pwny-CTF CTF, pwn category. Main technique: format-string. %s vs %lx on a stack secret: if the secret is the value placed on the stack (not a pointer to it), %s would crash by dereferencing this value as an address. We read the raw value with %lx/%p, then we decode it in little-endian (the least significant byte first -> 73 = s arrives first).

## Statement and artefacts
This challenge uses the stack read primitive. Reference the slides!

```nc chal.sigpwny.com 1381```

**Author**: Kevin Higgs

**Provided files / artifacts:**
- `work/stack_read (file, 16.8 KB)`
- `work/stack_read_patched (file, 16.8 KB)`

## Recognition signals
- If we observe greet() does printf(name), think of the input becoming the format string.
- Signal: As flag lives on the same stack, its bytes are among the arguments that printf believes it received.
- Signal: %s vs %lx on a stack secret: if the secret is the value placed on the stack (not a pointer to it), %s would crash by dereferencing this value as an address. We read the raw value with %lx/%p, then we decode it in little-endian (the least significant byte first -> 73 = s arrives first).

## Resolution method
1. **Locate FSB** — source shows `printf(name)` without `%s`: input is interpreted. (The 3 free hints confirm: flag on the stack, read it with `%p`, and `%s` will not work.)
2. **Scan the stack** — send `%lx.` × 20 as name → `sla(b"name?", b"%lx."*20)`, then `decode_leaks(leak_hex_int(rall()))` (helpers of `pwny.py`).
3. **Decode in little-endian** — two consecutive leaks contain ASCII text:
   - `leak[5] = 0x7b796e7770676973` → `73 69 67 70 77 6e 79 7b` = `sigpwny{`
   - `leak[6] = 0x7d2164336e7770` → `70 77 6e 33 64 21 7d` = `pwn3d!}`
4. **Paste** → `sigpwny{pwn3d!}` (15 characters = stack exactly `flag[16]`: 8 + 7 bytes).

See `work/pwny.py`. Scrolled: `sla("name?", "%lx."*20)` → `decode_leaks(leak_hex_int(rall()))` → spot `sigpwny{` / `pwn3d!}` in leaks 5-6.

1. **Flaw**

```c
char name[64], flag[16];
read_flag(flag);              // the flag is loaded on the main stack
while (1) {
    fgets(name, 64, stdin);
    greet(name);              // -> printf(name) == FORMAT STRING BUG
}
```
`greet()` does `printf(name)`: the entry becomes the **format string**. Since `flag` lives on the same stack, its bytes are among the arguments `printf` believes it received.

## Solve script
Script path: `scripts/pwny.py`

## Flag
sigpwny{pwn3d!}

## Lessons and reusable patterns
- %s vs %lx on a stack secret: if the secret is the value placed on the stack (not a pointer to it), %s would crash by dereferencing this value as an address. We read the raw value with %lx/%p, then we decode it in little-endian (the least significant byte first -> 73 = s arrives first).
- Recognize: source with printf(user) + a secret buffer (flag, pass) declared in the same function, no "win" function to call. Objective = read, not hijack execution.
- No need for offset_browser here: a simple %lx spray. enough, we can spot the flag by eye in the decoded leaks. (To target a specific index: %6$lx, %7$lx.)
- Leaks 0x2e786c252e786c25 (%lx.%lx.) = our own payload read from the stack, normal.
