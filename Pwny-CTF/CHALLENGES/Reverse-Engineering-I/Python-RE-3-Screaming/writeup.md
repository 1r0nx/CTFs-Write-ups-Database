---
title: "Python-RE-3-Screaming"
ctf: "Pwny-CTF"
category: "reverse"
difficulty: "Not specified"
points: 375
techniques: ["xor-cipher", "reverse-engineering", "encoding"]
tools: ["python"]
keywords: ["Python-RE-3-Screaming", "Pwny-CTF", "reverse", "xor-cipher", "reverse-engineering", "encoding", "python", "xor", "base64"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Reverse-Engineering-I/Python-RE-3-Screaming/notes.md"
---

# Python-RE-3-Screaming (Pwny-CTF, reverse)

## Summary
Challenge **Python-RE-3-Screaming** from the Pwny-CTF CTF, reverse category. Main technique: xor-cipher. Exec(base64(...)): base64 caches code, not a string — always decode to a file and parse, don't expect the plaintext flag.

## Statement and artefacts
I'm using a new obfuscation technique called screaming. Now you can't cheat my quiz! I think.

**Author**: Juniper

**Provided files / artifacts:**

## Recognition signals
- When a program redefines input/print/a builtin, all validation logic is hijacked: read these redefinitions first.

## Resolution method
1. `chal.py` = `exec(base64.b64decode(...).decode())`. Base64 therefore contains **not** the flag but **Python code**: decode it to a file rather than reading it online.
2. De-obfuscate: all variables are sequences of `A` of different lengths (34 distinct). Replacing each sequence of `A` with a short name (`v<i>_<length>`) makes the code readable. Warning: some sequences of `A` are in fact hexa constants (`0xAA`, `0xAAA`) eaten by the replacement.
3. Read the logic: `input` is **reassigned** to a function which, for each response, updates a global accumulator `v32_124`. At the end: `print("passed" if v32_124 == 0xf09c…00 else "…")`.
4. Key point: the combiner `S = lambda a: lambda b: a(a(b))` then `S(S)` applies its function **4 times**. For the question “What is the flag?” », the handler returns nothing (`None`) → each character is `v32_124 = (v32_124<<8) + transform(ord(c))`, where `transform` chains an XOR, `v30` applied 4x, and a permutation applied 16x (4×4).
5. `transform` is a **bijection** on `0..255` (verified: the 256 outputs are a permutation) → build the inverse table, split the target constant into bytes, remove the final `00` (from the end `<<8`), invert each byte. The `sigpwny{…}` portion comes out cleanly (the unreadable prefix comes from the bytes of the other questions, encoded differently).

## Solve script
Script path: `scripts/solve.py`

## Flag
sigpwny{n0t_3nough_0bfusc4t10n}

## Lessons and reusable patterns
- exec(base64(...)): base64 caches code, not a string — always decode to a file and parse, don't expect the plaintext flag.
- Obfuscation by indistinguishable identifiers (here A's, elsewhere l/I/1 or emojis): broken by replacing each unique identifier with a readable name (by length, order of appearance, etc.). A simple re.sub is enough.
- When a program redefines input/print/a builtin, all validation logic is hijacked: read these redefinitions first.
- A flag check via bijective house function byte by byte always inverts by tabulating the function to 0..255 (no need to understand it in detail). Reflex: test len(set(f(b) for b in range(256))) == 256.
- Combinator S(S) = applies the function 4 times: locate this type of fixed point rather than unrolling it by hand.
