---
title: "Elgamal-Oracle"
ctf: "Pwny-CTF"
category: "crypto"
difficulty: "Not specified"
points: 350
techniques: ["diffie-hellman", "elgamal", "malware-analysis"]
tools: ["netcat", "python"]
keywords: ["Elgamal-Oracle", "Pwny-CTF", "crypto", "diffie-hellman", "elgamal", "malware-analysis", "netcat", "python", "oracle"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Crypto/Elgamal-Oracle/notes.md"
---

# Elgamal-Oracle (Pwny-CTF, crypto)

## Summary
Challenge **Elgamal-Oracle** from the Pwny-CTF CTF, crypto category. Main technique: diffie-hellman. Reusing a private key in two protocols (here the a of DH AND of the ElGamal oracle) connects

## Statement and artefacts
You witness Alice and Bob do a Diffie-Hellman exchange. Now, you're given Alice's Elgamal decryption oracle which uses the same `a` that Alice used for her DH exchange with Bob. Can you find their shared secret?

Connect via `nc chal.sigpwny.com 1986`

We observe a Diffie-Hellman between Alice and Bob: `p`, `g=2`, `A = g^a`, `B = g^b`. The shared secret is `g^(ab) = B^a = A^b mod p`. Alice offers an **ElGamal decryption oracle** (usable **once**) which uses **the same `a`**. Find the shared secret.

**Provided files / artifacts:**

## Recognition signals
Not specified.

## Resolution method
1. **The reasoning**

The ElGamal decryption of a pair `(c1, c2)` with private key `a` is:
```
m = c2 · (c1^a)^{-1} mod p
```
(the oracle refuses `c2 == 1` to avoid reading `(c1^a)^{-1}` directly). We want `B^a` (= the shared secret, because `B = g^b` therefore `B^a = g^(ab)`).

Tip: put **`c1 = B`** and **`c2 = 2`** (anything ≠ 1). The oracle returns:
```
out = 2 · (B^a)^{-1} mod p
```
from which we isolate the secret:
```
B^a = 2 · out^{-1} mod p
```
One call is enough. We submit this `B^a` → flag `sigpwny{th3r3z_a_r3450n_e19am91_1snt_u53d_1n_7h3_w11d}`.

## Solve script
Script path: `scripts/elgamal-oracle.py`
Script path: `scripts/solve.py`

## Flag
sigpwny{th3r3z_a_r3450n_e19am91_1snt_u53d_1n_7h3_w11d}

## Lessons and reusable patterns
- Reusing a private key in two protocols (here the a of DH AND of the ElGamal oracle) connects
- Oracle which calculates c2·(c1^a)^{-1} -> by neutralizing c2 (putting it at a known constant) we
- Script: work/solve.py.
