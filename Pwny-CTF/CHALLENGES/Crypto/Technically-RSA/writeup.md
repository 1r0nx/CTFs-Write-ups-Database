---
title: "Technically-RSA"
ctf: "Pwny-CTF"
category: "crypto"
difficulty: "Not specified"
points: 200
techniques: ["rsa-small-exponent", "rsa-small-modulus"]
tools: ["factordb", "sympy", "python"]
keywords: ["Technically-RSA", "Pwny-CTF", "crypto", "rsa-small-exponent", "rsa-small-modulus", "factordb", "sympy", "python", "rsa"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Crypto/Technically-RSA/notes.md"
---

# Technically-RSA (Pwny-CTF, crypto)

## Summary
Challenge **Technically-RSA** from the Pwny-CTF CTF, crypto category. Main technique: rsa-small-exponent. Always look at n above all: size (factorizable if small?), parity, small factors

## Statement and artefacts
RSA specifies to use two prime numbers for p and q. Any prime numbers should be safe, right?

**Author**: Original by Surg, rewritten by Anakin

“RSA requires two prime numbers for p and q. Any firsts should be safe, right? » We have `c`, `e=3`, `n` (small, ~256 bits).

**Provided files / artifacts:**
- `work/message.txt (text, 174 B)`

## Recognition signals
- If we observe Always look at n above all, think about size (factorizable if small?), parity, small factors.

## Resolution method
1. **The reasoning**

RSA callback: `n = p*q` (prime p, q), `phi = (p-1)(q-1)`, private key `d = e^-1 mod phi`, decryption `m = c^d mod n`. Security is based on the **impossibility of factoring `n`**.

Here the trap is in “any prime”: **`2` is a prime number**. Looking at `n`, it **ends in 2** → `n` is **even** → one of the factors is `p = 2`. So `q = n/2`, and we check that `q` is prime. The factorization is immediate, RSA falls:
```
phi = (2-1)*(q-1) = q-1
d   = e^-1 mod phi
m   = c^d mod n  ->  sigpwny{d0_n0t_u5e_tw0}
```

## Solve script
Script path: [scripts/solve.py](scripts/solve.py)

## Flag
sigpwny{d0_n0t_u5e_tw0}

## Lessons and reusable patterns
- Always look at n above all: size (factorizable if small?), parity, small factors
- A first “valid” but too small or particular (2, first close, p=q...) destroys RSA.
- CTF RSA reflex: try factorint(n) / factordb; check GCD between several n; p≈q (Fermat).
- Script: work/solve.py.
