---
title: "Lockpicker"
ctf: "Pwny-CTF"
category: "crypto"
difficulty: "Not specified"
points: 200
techniques: ["rsa-small-modulus"]
tools: ["tar", "python"]
keywords: ["Lockpicker", "Pwny-CTF", "crypto", "rsa-small-modulus", "tar", "python", "rsa", "padding"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Crypto/Lockpicker/notes.md"
---

# Lockpicker (Pwny-CTF, crypto)

## Summary
Challenge **Lockpicker** from the Pwny-CTF CTF, crypto category. Main technique: rsa-small-modulus. Many RSA keys from the same source poorly generated = test the GCD in pairs. A common factor

## Statement and artefacts
I've hacked into a data server and gotten 1000 public RSA keys. I know that the user of one of them has encrypted the flag (with PKCS1_OAEP padding) but I couldn't get any of their private keys! Is this enough to decrypt the flag?

1000 RSA public keys. The flag was encrypted (PKCS1_OAEP) with one of them. We have **no private key**. Enough to decipher?

**Provided files / artifacts:**
- `work/flag_enc (file, 345 B)`
- `work/keys.tar.xz (archive, 264.7 KB)`

## Recognition signals
- Signal: OAEP is a verified decryption padding: it throws an error if the key/ciphertext does not.

## Resolution method
1. **The reasoning**

RSA security is based on the impossibility of factoring `n = p·q`. But if a key generator has **bad entropy**, two different users can draw the **same prime**. So their modules `n_i` and `n_j` share this factor, and:
```
p = gcd(n_i, n_j) > 1
```
is calculated **instantly** (Euclid), while factoring a single `n` is infeasible. This is the famous “Mining your Ps and Qs” (Heninger et al.) weakness of poorly generated keys.

1. Load the 1000 modules.
2. **GCD in pairs** (here double loop, ~500k GCD of 2048 bits = a few seconds; in reality we use one *batch GCD* per product tree for large sets). We find `gcd(n_145, n_694) = p` (shared factor of 1024 bits).
3. Factor `n = p·q`, calculate `d = e^{-1} mod (p-1)(q-1)`, reconstruct private key.
4. Decrypt `flag_enc` into **PKCS1_OAEP** (OAEP fails properly if it is not the right key → we try the two keys of the pair; `pubkey-145` gives the flag).

```
```

## Solve script
Script path: `scripts/solve.py`

## Flag
sigpwny{more_keys_less_secure}

## Lessons and reusable patterns
- Many RSA keys from the same source poorly generated = test the GCD in pairs. A common factor
- For very large sets: batch GCD (product tree + remainder tree) quasi-linear,
- OAEP is a verified decryption padding: it throws an error if the key/ciphertext does not
- Script: work/solve.py (extract keys.tar.xz into a temporary folder).
