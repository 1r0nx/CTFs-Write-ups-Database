---
title: "Tyco"
ctf: "2026-hiCTF"
category: "crypto"
difficulty: "medium"
points: null
techniques: ["rsa-small-exponent", "rsa-related-message"]
tools: ["unzip", "python-flint", "sage", "python"]
keywords: ["Tyco", "hiCTF", "crypto", "rsa-small-exponent", "rsa-related-message", "unzip", "python-flint", "sage", "python", "zip", "rsa"]
status: "solved"
has_script: true
source: "hiCTF/Cryptography/Tyco/notes.md"
---

# Tyco (hiCTF, crypto)

## Summary
Challenge **Tyco** from the hiCTF CTF, crypto category. Main technique: rsa-small-exponent. Launch: <venv>/bin/python solve.py chall.txt (requires pip install python-flint).

## Statement and artefacts
**Provided files / artifacts:**
- `tyco.zip (archive, 690 B)`
- `work/chall.txt (text, 634 B)`

## Recognition signals
- Signal: Franklin-Reiter attack (linked messages encrypted with the same N and the same e).
- Signal: Naming trap: the d in the script is not the RSA private exponent, just an offset.
- Signal: python-flint: fmpz_mod_poly.gcd() raises DomainError if the module is not prime -> write the Euclid loop yourself.

## Resolution method
1. **The challenge (chall.py)**

```python
N = getPrime(256) * getPrime(256)      #512-bit RSA
e = getPrime(16)                        # here e = 56263
r = bytes_to_long(flag)
d = random.randrange(1, N)              # PUBLISHED (≠ private exponent!)
t1 = pow(r, e, N)
t2 = pow(r + d, e, N)
print(N, e, d, t1, t2)
```
**Flaw**: two messages linked by a **known** relationship (`m2 = m1 + d`) encrypted with the **same N and the same e**.

| Stage | Command | What it reveals |
|---|---|---|
| 1 | `unzip -p tyco.zip` | RSA, two ciphers of `r` and `r + d`, `d` known → Franklin-Reiter |
| 2 | `which sage` / `import flint` | Neither Sage nor FLINT → `python-flint` installed in a venv (scratchpad) |
| 3 | `python solve.py chall.txt` (v1, `P1.gcd(P2)`) | FLINT refuses: its fast PGCD requires a **prime** module |
| 4 | `python solve.py chall.txt` (v2, Manual Euclid) | PGCD of degree 1 → `r`, check `t1`/`t2` OK, flag (14 min of calculation) |

**Principle**: `r` is the common root of
- `P1(x) = x^e − t1`
- `P2(x) = (x + d)^e − t2`

therefore `pgcd(P1, P2) = a·x + b` (almost always) and `r = −b / a mod N`. No factorization of N.

## Solve script
Script path: `scripts/solve.py`

## Flag
hiCTF{your_ai_slop_bores_me}

## Lessons and reusable patterns
- Recognize: two RSA encrypted messages linked by a known affine relation (m2 = a·m1 + b), same N, same e -> Franklin-Reiter.
- Cost ∝ e: e = 3 -> instantaneous; e ≈ 56,000 -> Naive Euclid ≈ e² operations (~14 min here). A half-GCD (Sage: P1.gcd(P2) over Zmod(N)[x]) would do it in seconds.
- Naming pitfall: the d in the script is not the RSA private exponent, just an offset.
- python-flint: fmpz_mod_poly.gcd() raises DomainError if the module is not prime -> write the Euclid loop yourself.
