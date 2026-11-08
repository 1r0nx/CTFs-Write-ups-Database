---
title: "Double-Nonce"
ctf: "Pwny-CTF"
category: "crypto"
difficulty: "Not specified"
points: 200
techniques: ["aes-cbc", "aes-ctr", "elliptic-curve"]
tools: ["radare2", "sage", "python"]
keywords: ["Double-Nonce", "Pwny-CTF", "crypto", "aes-cbc", "aes-ctr", "elliptic-curve", "radare2", "sage", "python", "https", "aes", "lattice", "nonce", "cbc"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Crypto/Double-Nonce/notes.md"
---

# Double-Nonce (Pwny-CTF, crypto)

## Summary
Challenge **Double-Nonce** from the Pwny-CTF CTF, crypto category. Main technique: aes-cbc. Reused ECDSA/DSA nonce = broken private key (two equations, two unknowns k and d).

## Statement and artefacts
This challenge is meant to show you how to exploit nonce reuse in ECDSA. Try to follow the formulas in https://github.com/elikaski/ECC_Attacks?tab=readme-ov-file#Reusing-the-same-value-of-k-in-different-signatures

Two messages signed in ECDSA (curve secp256k1), same key `d`. `out.txt` gives the two signatures, the IV and the flag encrypted in AES-CBC. The description points to the “reuse of `k`” attack.

**Provided files / artifacts:**
- `work/out.txt (text, 561 B)`

## Recognition signals
Not specified.

## Resolution method
1. **ECDSA reminder**

For a hash `z`, a random **nonce** `k`, a private key `d`: `r = (k·G).x mod n` and `s = k⁻¹·(z + d·r) mod n`. The `k` nonce must be **unique and secret** for each signature. If it is reused, it is immediately visible: **`r` is identical** (because `r` only depends on `k·G`). This is `r1 == r2`.

2. **The reasoning**

Two signatures with the **same `k`**:
```
s1 = k⁻¹(z1 + d·r)
s2 = k⁻¹(z2 + d·r)
s1 - s2 = k⁻¹(z1 - z2)      ⟹   k = (z1 - z2) / (s1 - s2)  mod n
then s1 = k⁻¹(z1 + d r) ⟹ d = (s1 k - z1) / r mod n
```
We recover `d`. Here `aes_key = d.to_bytes(32)`, so we decrypt the flag directly in AES-CBC: `sigpwny{r3duc3_r3use_rec5cl3}`.

## Solve script
Script path: `scripts/chal.sage`
Script path: `scripts/solve.py`

## Flag
sigpwny{r3duc3_r3use_rec5cl3}

## Lessons and reusable patterns
- Reused ECDSA/DSA nonce = broken private key (two equations, two unknowns k and d).
- Variant: partially known/biased nonces -> network attack (lattice/HNP).
- Good practice: RFC 6979 deterministic nonce (k = HMAC(d, z)), never weak RNG.
- Script: work/solve.py (pure Python, no need for sage despite the original.sage).
