---
title: "1-Manipulate"
ctf: "Pwny-CTF"
category: "pwn"
difficulty: "Not specified"
points: 150
techniques: ["buffer-overflow", "stack-canary", "pie-bypass"]
tools: ["pwntools", "python"]
keywords: ["1-Manipulate", "Pwny-CTF", "pwn", "buffer-overflow", "stack-canary", "pie-bypass", "pwntools", "python", "canary", "pie", "stack", "padding"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Pwn/1-Manipulate/notes.md"
---

# 1-Manipulate (Pwny-CTF, pwn)

## Summary
Challenge **1-Manipulate** from the Pwny-CTF CTF, pwn category. Main technique: buffer-overflow. Write a precise value in an overflow -> p64(value) (never by hand: handles little-endian and 8-byte padding).

## Statement and artefacts
Can you pwn this problem? Look at the challenge.c and pwn writeup for hints!

Code (challenge.c):
  char name[40];
  uint64_t number = 0xdeadbeef;   // just after name
  gets(name);                     //overflow
  if (number == 0xcafebabe) print_flag();   // you need number == 0xcafebabe EXACTLY
  else "Try again"

Build: gcc -O0 -fno-stack-protector (no canary). PIE, unstripped.

**Provided files / artifacts:**
- `Makefile (file, 118 B)`
- `challenge (file, 19.0 KB)`
- `challenge_patched (file, 19.0 KB)`

## Recognition signals
- Signal: Continuation of 0 - Overflow: here it is not enough to change number, you must set it exactly to 0xcafebabe.

## Resolution method
1. Payload = `padding up to number` + `p64(0xcafebabe)`.
2. **Offset** = 48 (the 40 bytes of `name` + 8 of alignment padding).
3. **Little-endian**: `p64(0xcafebabe)` writes `be ba fe ca 00 00 00 00` → number = `0x00000000cafebabe` ✔.
4. `sla(b"name?", b"A"*48 + p64(0xcafebabe))` → `print_flag()`.

1. **Flaw**

```c
char name[40];
uint64_t number = 0xdeadbeef;        // just after name
gets(name);                          // overflow (no canary)
if (number == 0xcafebabe) print_flag();   // PRECISE value required
```
Continuation of 0 - Overflow: here it is not enough to change `number`, it must be set **exactly to `0xcafebabe`**.

## Discarded approaches
- Find the offset properly: cyclic(200) then cyclic_find(<value at crash>).

## Solve script
Script path: [scripts/pwny.py](scripts/pwny.py)

## Flag
sigpwny{1_think_you_should_use_fgets_not_gets}

## Lessons and reusable patterns
- Write a precise value in an overflow -> p64(value) (never by hand: handles little-endian and 8-byte padding).
- x86-64 = little-endian: low byte first in memory.
- Same binary as 0 - Overflow but condition == instead of!= -> exact write control.
