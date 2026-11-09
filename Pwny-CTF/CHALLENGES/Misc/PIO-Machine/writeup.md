---
title: "PIO-Machine"
ctf: "Pwny-CTF"
category: "misc"
difficulty: "easy"
points: 350
techniques: ["crypto", "password-cracking", "reverse-engineering", "web-exploitation"]
tools: ["tar", "gcc", "python"]
keywords: ["PIO-Machine", "Pwny-CTF", "misc", "tar", "gcc", "python", "https", "oracle"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Misc/PIO-Machine/notes.md"
---

# PIO-Machine (Pwny-CTF, misc)

## Summary
Challenge **PIO-Machine** from the Pwny-CTF CTF, misc category. The same binary/game can hide several flags indexed by challenges

## Statement and artefacts
Can you reverse the *other* hidden flag in the Deere Game?

See: https://tutoduino.fr/en/pio-rp2040-en/

**Provided files / artifacts:**
- `work/code.tar.gz (archive, 12.8 KB)`

## Recognition signals
Not specified.

## Resolution method
1. **The idea**

Same game as [[Haybales]] (same `code.tar.gz`, “Deere Game”): this is the **second** (“*other*”) flag, the one kept by the **PIO program of the RP2040**. You need the key `key` such as `pio_mix(key) == 0x122c5bf4`, then `SHA-256(key) ⊕ encoded`.

2. **Method (summary — details in Haybales/notes.md)**

1. `deere_chal.py:decode_flag()`, branch `elif self.pio_mix(key) == 0x122c5bf4`.
2. `pio_mix` executes the PIO program `simple_pio` (8×: `out(x,1)`, `out(y,3)`, `jmp(y_dec)` if x==1 — **unconditional decrement, wrap to 0xFFFFFFFF**, `mov(y,~y)`, `in(y,3)`, `in(x,1)`).
3. **Brute force** of the 2^32 keys in C (`work/pio_brute.c`, ~50 s, shift-left by default), then decryption of each candidate by `SHA-256(key_le)[:27] ⊕ encoded`: only the good key (`0x8661eb95`) gives an ASCII text → the flag.

## Solve script
Script path: [scripts/pio_brute.c](scripts/pio_brute.c)
Script path: [scripts/solve.py](scripts/solve.py)

## Flag
sigpwny{th3_pio_1s_4w3s0m3}

## Lessons and reusable patterns
- The same binary/game can hide several flags indexed by challenges
- Emulation of a PIO RP2040 + decryption oracle: see [[Haybales]] for the
