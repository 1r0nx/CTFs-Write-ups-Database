---
title: "Deprecated-Specific-stack-overflow"
ctf: "Pwny-CTF"
category: "pwn"
difficulty: "Not specified"
points: 150
techniques: ["buffer-overflow"]
tools: ["netcat", "python"]
keywords: ["Deprecated-Specific-stack-overflow", "Pwny-CTF", "pwn", "buffer-overflow", "netcat", "python", "stack", "padding", "oracle"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Pwn/Deprecated-Specific-stack-overflow/notes.md"
---

# Deprecated-Specific-stack-overflow (Pwny-CTF, pwn)

## Summary
Challenge **Deprecated-Specific-stack-overflow** from the Pwny-CTF CTF, pwn category. Main technique: buffer-overflow. Condition == vs!=: == -> write the exact value with p64(v) at the correct offset;!= (see Deprecated - stack overflow) -> anything will do.

## Statement and artefacts
Can you pwn this program? Look in challenge.c for hints!

`nc chal.sigpwny.com 1375`

**Provided files / artifacts:**
- `work/Dockerfile (file, 580 B)`
- `work/challenge (file, 19.4 KB)`
- `work/challenge_patched (file, 19.4 KB)`

## Recognition signals
- Signal: Calibrate the offset when the code returns the value obtained: it is a free oracle (send a known pattern, read what lands in number, adjust the padding). Here 40, not the “naive” 32 (compiler alignment).

## Resolution method
1. **Binary**

- `main()`: `char name[32];` then `uint64_t number = 0;`. Reading by **`gets(name)`** (unbounded).
- Victory: `if (number == 0x4142434445464748) print_flag();` → you need the **precise value**, not just non-zero.
- The source insists on **endianness** (comment + link): on a little-endian system, the least significant byte leaves first.

1. Overflow `name` then write `0x4142434445464748` to `number`.
2. **Offset = 40** (step 32): `32` bytes of `name` + `8` of alignment / saved RBP before `number`. We match it with the return of the program (`The number is 0x... right now` displays what we wrote → oracle to get it right).
3. `p64()` encodes in **little-endian** alone → on the wire the bytes are `48 47 46 45 44 43 42 41` = `"HGFEDCBA"`.

```python
payload = b"A" * 40 + p64(0x4142434445464748)
sla(b"!", payload)
```

## Solve script
Script path: [scripts/pwny.py](scripts/pwny.py)

## Flag
sigpwny{awesome_job_dont_forget_about_endianness}

## Lessons and reusable patterns
- Condition == vs!=: == -> write the exact value with p64(v) at the correct offset;!= (see Deprecated - stack overflow) -> anything will do.
- Endianness: p64(0x41..48) -> bytes sent in reverse (48 first). Typing "ABCDEFGH" would give 0x4847464544434241, therefore wrong. Let p64 handle it.
- Calibrate the offset when the code returns the value obtained: it is a free oracle (send a known pattern, read what lands in number, adjust the padding). Here 40, not the “naive” 32 (compiler alignment).
