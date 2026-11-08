---
title: "Bug-Bounty-1"
ctf: "Pwny-CTF"
category: "pwn"
difficulty: "Not specified"
points: 100
techniques: ["format-string", "stack-canary"]
tools: ["pwntools", "netcat", "python"]
keywords: ["Bug-Bounty-1", "Pwny-CTF", "pwn", "format-string", "stack-canary", "pwntools", "netcat", "python", "canary", "stack"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/PWN-I/Bug-Bounty-1/notes.md"
---

# Bug-Bounty-1 (Pwny-CTF, pwn)

## Summary
Challenge **Bug-Bounty-1** from the Pwny-CTF CTF, pwn category. Main technique: format-string. Gets() always writes a final \0 after the entry: filling a buffer with N bytes already overflows by 1 byte (off-by-one / null-byte overflow).

## Statement and artefacts
Huzzah, what a historic day! An unpaid staff engineer at SUPERMEGACORP believes they've written the very first C program without any critical vulnerabilities. What a time to be alive!

SUPERMEGACORP has offered a $500 bug bounty if anyone can prove them wrong...

(the CEO has already fled the country with the company's assets, so the bounty is coming out of the janitor's pension fund)

`nc chal.sigpwny.com 1343`

**author**: Akhil

**Provided files / artifacts:**
- `work/Makefile (file, 118 B)`
- `work/challenge (file, 19.7 KB)`

## Recognition signals
- Signal: Compiled with -fno-stack-protector (no canary) and -O0: the stack keeps the expected order, number is pasted just after name.
- Signal: The program even draws the stack before/after input.

## Resolution method
1. Read `challenge.c`: `gets(name)` on 40 bytes, then test `number!= 0xcafebabe` → no need for a precise value, just a **different** value.
2. Read the stack displayed “before”: `name` to `…d0a0`, `number` to `…d0c8` → `0xc8 - 0xa0 = 40`: `number` starts right after `name`.
3. `starter.py` as is: `b"A" * 40` sent with `sendline` → flag.
4. Why 40 is enough: `gets()` always writes a zero byte `\0` after what it has read, here just after the 40 `A`, therefore on the least significant byte of `number`. Before: `be ba fe ca 00 00 00 00` (`0xcafebabe`) → after: `00 ba fe ca …` (`0xcafeba00`) ≠ `0xcafebabe` ✔.

1. **Order ready**

```bash
python3 -c 'from pwn import *; io=remote("chal.sigpwny.com",1343); io.sendlineafter(b"> ", b"A"*40); print(io.recvall(timeout=2))'
```

2. **Flaw**

```c
uint64_t number = 0xcafebabe;   // just after name in memory
char name[40];
gets(name);                     // no size limit
if (number != 0xcafebabe) print_flag();   // just CHANGE number
```
Compiled with `-fno-stack-protector` (no canary) and `-O0`: the stack keeps the expected order, `number` is stuck just after `name`. The program even draws the stack before/after typing.

## Solve script
Script path: `scripts/starter.py`

## Flag
sigpwny{lol_we_dont_give_our_janitors_pensions}

## Lessons and reusable patterns
- gets() always writes a final \0 after the entry: filling a buffer of N bytes already overflows by 1 byte (off-by-one / null-byte overflow).
- Read the condition:!= (change the value) vs == (exact value, see 1 - Manipulate -> p64).
- The program draws the stack: the offset is read directly (address difference), no need for cyclic.
- Recognize: C source provided + gets/scanf("%s") + local variable tested after entry.
