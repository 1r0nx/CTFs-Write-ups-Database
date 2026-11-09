---
title: "Merkle"
ctf: "Pwny-CTF"
category: "crypto"
difficulty: "Not specified"
points: 250
techniques: ["diffie-hellman", "rf"]
tools: ["python"]
keywords: ["Merkle", "Pwny-CTF", "crypto", "diffie-hellman", "rf", "python"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Crypto/Merkle/notes.md"
---

# Merkle (Pwny-CTF, crypto)

## Summary
Challenge **Merkle** from the Pwny-CTF CTF, crypto category. Main technique: diffie-hellman. DH is only safe if the private exponents are large and random (and p well chosen). A

## Statement and artefacts
We've heard plenty about Alice and Bob, but now we're going to play the role of Eve! Eve plays the role of the eavesdropper and intercepts all communication between Alice and Bob.

Given all the parameters in `eve.txt` compute Alice and Bob's shared secret key. The variable names are the same as the common variable names found in the previous link. The flag is in the format `sigpwny{16 most significant digits of the secret key}`.

Fun Fact: Hellman suggested the algorithm be called Diffie–Hellman–**Merkle** key exchange in recognition of Ralph Merkle's contribution to the invention of public-key cryptography (Wikipedia)

We play Eve (the spy) who intercepts a Diffie-Hellman exchange. `eve.txt` gives `g`, `p`, `A`, `B`. Calculate the shared secret of Alice and Bob. Flag = `sigpwny{16 most significant digits of the secret}`.

**Provided files / artifacts:**
- `work/eve.txt (text, 1.4 KB)`

## Recognition signals
- Signal: DH is only safe if the private exponents are large and random (and p well chosen). One.

## Resolution method
1. **Diffie-Hellman reminder**

Audience: `g`, `p`. Alice draws a secret `a` and publishes `A = g^a mod p`. Bob pulls `b` and publishes `B = g^b mod p`. The **shared secret** is `s = g^(a·b) mod p = A^b mod p = B^a mod p`. A spy sees `g, p, A, B` but not `a`, `b`. To break, it would be necessary to solve the **discrete logarithm** (find `a` such as `g^a = A mod p`), known to be very hard for a large `p`.

2. **The reasoning**

The clue says it: here the private exhibitors are **small**, `2 <= a, b <= 100000`. The discrete log therefore becomes trivial by **brute force**: we calculate `g^i mod p` for `i = 2, 3,...` (by multiplying by `g` at each step, incremental) until falling back on `A`. We find `a = 65537`. Then the secret:
```
s = B^a mod p
```
The first 16 digits of `s` result in `sigpwny{1479671363201260}`.

## Solve script
Script path: [scripts/solve.py](scripts/solve.py)

## Flag
sigpwny{1479671363201260}

## Lessons and reusable patterns
- DH is only safe if the private exponents are large and random (and p well chosen). A
- Raw discrete log: incremental pow, ~10^5 iterations = instantaneous. For smooth p-1:
- Read the format of the flag: here these are not bytes but the decimal digits of the secret.
- Script: work/solve.py.
