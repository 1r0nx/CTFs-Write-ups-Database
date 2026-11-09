---
title: "Rocinate"
ctf: "2026-hiCTF"
category: "crypto"
difficulty: "hard"
points: null
techniques: ["rsa-small-exponent", "prng-mt19937", "lcg", "buffer-overflow", "prng-prediction"]
tools: ["python"]
keywords: ["Rocinate", "hiCTF", "crypto", "rsa-small-exponent", "prng-mt19937", "lcg", "buffer-overflow", "prng-prediction", "python", "zip", "rsa", "mt19937"]
status: "solved"
has_script: true
source: "hiCTF/Cryptography/Rocinate/notes.md"
---

# Rocinate (hiCTF, crypto)

## Summary
Challenge **Rocinate** from the hiCTF CTF, crypto category. Main technique: rsa-small-exponent. “🤭😂”; rocinate.zip -> chall.py + chall.txt.

## Statement and artefacts
“🤭😂”; rocinate.zip -> chall.py + chall.txt.

**Provided files / artifacts:**
- `rocinate.zip (archive, 115.7 KB)`
- `work/chall.txt (text, 243.0 KB)`

## Recognition signals
- Signal: Mersenne Twister (Python random) predictable -> find state from published outputs, then go back in time to secrets.
- Signal: random = MT19937, non-cryptographic: r, e, a, b, c_i come out; we publish a, b and 100 c_i ≈ 210,000 output bits (we need ~20,000).
- Signal: Z_i is not reduced mod N (~4090 bits) -> Z_i / r_i = s^c_i mod N is an exact division as soon as we know r_i.
- If we observe a false temperature (starting value overwritten in the loop << 7), consider finding it by unit test against random.
- If we observe Untwist “entire block”: loses the 31 weak bits of the 1st word, think about replacing it with step back word by word.
- Signal: Validation on 16 words insufficient: several combinations of 9 bits passed, 25 words moved back false -> require regenerating the entire known sequence.

## Resolution method
1. | Step | Action | Result |
|---|---|---|
| 1 | `inspect.getsource(random.Random._randbelow_with_getrandbits)` | `randint(1, N) = 1 + getrandbits(2047)` with **rejection** if ≥ N (22%); 64 32-bit words, least significant first, last word `>> 1` (31 bits known) |
| 2 | Window of 10 consecutive `c` = 624 words, 9 unknown bits → 2⁹ tries, `untemper`, `setstate` | Condition regained; **validated by regenerating all the following c** (rejects included) |
| 3 | Rewind **word by word** (reverse MT recurrence) then simulate `randint` | `r, e, a, b` found 1792 words before the window |
| 4 | LCG → `r_i`; checks `r_i | Z_iZXQPH0QXZr_i^e = T_i` (100/100) | OK |
| 5 | `y_i = Z_i // r_i`; Bézout `u c_i + v c_j = 1` → `s = y_i^u · y_j^v mod N` | flag |

**Backtrack word by word**: `x[k+624] = x[k+397] ^ f(MSB(x[k]) | low31(x[k+1]))`. `t = x[k+624] ^ x[k+397]`; if `t` has its strong bit at 1: `y = ((t ^ 0x9908b0df) << 1) | 1`, otherwise `y = t << 1`. So `x[m] = MSB(y(m)) | low31(y(m-1))`.

2. **The challenge and its flaws**

```python
N = getPrime(1024) * getPrime(1024)            # safe hazard (Crypto)
r = random.randint(1, N); e = random.randint(1, N)
a, b = random.randint(1, N), random.randint(1, N)
Rs : r_{i+1} = a*r_i + b mod N                 # LCG, 100 values
Cs = [random.randint(1, N) for _ in range(100)]
Zs = [ri * pow(s, ci, N) ...]                   # s = flag
Ts = [pow(ri, e, N) ...]
print(a, b, N, Zs, Cs, Ts)
```
1. **`random` = MT19937, non-cryptographic**: `r`, `e`, `a`, `b`, `c_i` come out; we publish a, b and 100 c_i ≈ 210,000 output bits (~20,000 are needed).
2. **`Z_i` is not reduced mod N** (~4090 bits) → `Z_i / r_i = s^c_i mod N` is an **exact division** as soon as we know `r_i`.

3. **Bugs encountered (and lesson)**

- `untemper` false (start value overwritten in `<< 7` loop) → found by **unit test against `random`**.
- Untwist “entire block”: loses the weak 31 bits of the 1st word → replaced by word-by-word backwards.
- Insufficient validation on 16 words: several combinations of 9 bits passed, 25 words moved back wrong → require **regenerating the entire known sequence**.
- Recursive Bézout → stack overflow → iterative version.
- **Lesson**: first generate a **test instance with known flag** (`random.seed(1234)` + modified `chall.py`) and compare to the real suite.

## Solve script
Script path: [scripts/solve.py](scripts/solve.py)

## Flag
hiCTF{lmaoooo_w0t???y0u_d1d_17_??435p37++}

## Lessons and reusable patterns
- Recognize: import random in a crypto challenge + lots of published random values -> breakable MT19937 (624 32-bit outputs), forward and backward.
- Know the exact division of calls: getrandbits(k) (lowest words first, last truncated), randint / randrange (rejection), random() (53 bits over 2 words).
- An unreduced value modulo N (product of integers) = leakage: exact division possible.
- Ready-to-use tools for simple cases (624 complete consecutive words): randcrack; for missing bits/holes: bit brute-force or GF(2) solver.
