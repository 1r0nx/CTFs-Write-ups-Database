---
title: "Python-RE-2-Challenge-Store"
ctf: "Pwny-CTF"
category: "reverse"
difficulty: "Not specified"
points: 225
techniques: ["xor-cipher", "reverse-engineering"]
tools: ["python"]
keywords: ["Python-RE-2-Challenge-Store", "Pwny-CTF", "reverse", "xor-cipher", "reverse-engineering", "python", "xor"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Reverse-Engineering-I/Python-RE-2-Challenge-Store/notes.md"
---

# Python-RE-2-Challenge-Store (Pwny-CTF, reverse)

## Summary
Challenge **Python-RE-2-Challenge-Store** from the Pwny-CTF CTF, reverse category. Main technique: xor-cipher. Look for the branch that touches the flag before reading the whole program: a lot of code in RE is just filler. Grep flag, data, final comparisons.

## Statement and artefacts
I found this new store that sells challenges, but I heard they might also sell flags.

**Author**: Juniper

**Provided files / artifacts:**

## Recognition signals
- Signal: Loop of N iterations at the opaque counter (while c!= val: c = c*k % 2**n): if the applied transformation is of small order, do not calculate N — apply the opposite until the plaintext (flag format) appears. Reflex identical to “apply a permutation until the readable fixed point”.

## Resolution method
1. Read `chal.py` in full and identify where the flag occurs: only in `storeExamine()` option 5. The rest (`storeBuy`, `storeRestock`, `storeThreaten`…) is decoration intended to drown out the logic.
2. In option 5, after having `rev 1` in the inventory: the entry is transformed N times then compared to `data` (which ends with `flag`). The transformation by element is `T(x) = randomize3(randomize2(randomize3(x)))`:
   - `randomize3(x) = x ^ 24 ^ 1 ^ 73 ^ 5` → a simple XOR (its own inverse).
   - `randomize2(x)` does **rotate the 3 low nibbles** (n0→n1→n2→n0), bits ≥ 12 unchanged → bijection to 12 bits.
3. `flag[]` and `data[]` are therefore values **already transformed N times**. To read the flag: invert `T` on each element. Reverse: `Tinv(x) = randomize3(derand2(randomize3(x)))`, where `derand2` turns the nibbles the other way.
4. The N (number of iterations of `while c!= 60: c = (c*0x1337)%2**32`) is enormous (almost a discrete log) — **no need to calculate it**: `T` is a bijection of **small order** on the domain, so applying `Tinv` until you end up with readable ASCII is enough. Here **2 applications** give `sigpwny{d0nt_just_l00k_buy_buy_buy}`.

## Solve script
Script path: `scripts/mod.py`
Script path: `scripts/solve.py`

## Flag
sigpwny{d0nt_just_l00k_buy_buy_buy}

## Lessons and reusable patterns
- Look for the branch that touches the flag before reading the whole program: a lot of code in RE is just filler. Grep flag, data, final comparisons.
- A chain of transformations containing only XOR + bit permutation is always a bijection -> invertible element by element, without brute force.
- Loop of N iterations with opaque counter (while c!= val: c = c*k % 2**n): if the applied transformation is of small order, do not calculate N — apply the opposite until the plaintext (flag format) appears. Reflex identical to “apply a permutation until the readable fixed point”.
- Detect plaintext: all bytes in 0x20..0x7e and starts with sigpwny{.
