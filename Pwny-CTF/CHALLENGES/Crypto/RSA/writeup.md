---
title: "RSA"
ctf: "Pwny-CTF"
category: "crypto"
difficulty: "Not specified"
points: 150
techniques: ["rsa-small-exponent", "rsa-small-modulus", "rsa-wiener", "rsa-padding-oracle", "encoding"]
tools: ["openssl", "factordb", "pycryptodome", "python"]
keywords: ["RSA", "Pwny-CTF", "crypto", "rsa-small-exponent", "rsa-small-modulus", "rsa-wiener", "rsa-padding-oracle", "encoding", "openssl", "factordb", "pycryptodome", "python", "base64", "padding"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Crypto/RSA/notes.md"
---

# RSA (Pwny-CTF, crypto)

## Summary
Challenge **RSA** from the Pwny-CTF CTF, crypto category. Main technique: rsa-small-exponent. RSA = safe only because factoring n is infeasible. Do we give p (or q, or φ, or d)? -> everything collapses.

## Statement and artefacts
RSA is an asymmetric encryption (public key to encrypt, private key to decrypt). Public key = (n, e) with n = p*q (product of two large primes) and e the public exponent (often 65537). Private key = (p, q, d) with d = modular inverse of e mod totient(n) = (p-1)(q-1). Factoring n is infeasible... EXCEPT that here we are given one of the two prime factors p! The goal: reconstruct the private key from the public key + p, and decrypt the ciphertext.

Note: public.pem = public key in PEM format (base64). Use PyCryptodome to import it.

- Public key `public.pem` = (n, e): n = 2048 bits, e = 65537.
- File `p` = one of the two prime factors (1024 bits), with `n % p == 0`.
- `ciphertext` encrypted in RSA **PKCS#1 v1.5** (seen in `rsa.py`).

**Provided files / artifacts:**
- `ciphertext (file, 256 B)`
- `e (file, 6 B)`
- `n (file, 618 B)`
- `p (file, 309 B)`
- `private.pem (file, 1.6 KB)`
- `public.pem (file, 450 B)`
- `q (file, 310 B)`

## Recognition signals
- Signal: Trap: // for the division of large integers (never /). Respect the padding when decrypting.

## Resolution method
1. **Method (RSA math)**

1. `q = n // p` (ENTER division `//`, not `/` which would give a false float). Check: `p*q == n`.
2. `φ(n) = (p-1)*(q-1)` (the totient).
3. `d = pow(e, -1, φ(n))` (modular inverse of e mod φ) — or the lambda `MMI` provided.
4. Reconstruct the key and decrypt (PKCS#1 v1.5 depadding).

2. **Path A — PyCryptodome (provided by rsa.py)**

```python
q = n // p
d = pow(e, -1, (p-1)*(q-1))
privateKey = RSA.construct((n, e, d, p, q))   # deduces dP, dQ, qInv alone
plaintext = PKCS1_v1_5.new(privateKey).decrypt(ciphertext, None)
```

3. **Path B — RsaCtfTool + openssl (the one used)**

```bash
RsaCtfTool -n <n> -e 65537 -p <p> -q <q> --private --output private.pem   #(--output, not -B)
openssl pkeyutl -decrypt -inkey private.pem -in ciphertext                # padding PKCS#1 v1.5 by default
```
⚠️ Do NOT use `--uncipher` from RsaCtfTool here: it does raw RSA (textbook) → the PKCS#1 v1.5 padding would not be removed. Going through `openssl pkeyutl -decrypt` manages depadding.

Flag: `sigpwny{l34rn1ng_mod3rn_crypt0}`.

## Solve script
Script path: [scripts/rsa.py](scripts/rsa.py)

## Flag
sigpwny{l34rn1ng_mod3rn_crypt0}

## Lessons and reusable patterns
- RSA = safe only because factoring n is infeasible. Do we give p (or q, or φ, or d)? -> everything collapses.
- An RSA PKCS#1 private key = 9 values (n, e, d, p, q, dP, dQ, qInv); RSA.construct((n, e, d, p, q)) or RsaCtfTool calculate the rest.
- Other classic RSA attacks in CTF: factordb (n already factored), small e (th root), Wiener (small d), common module, Fermat (near p, q). RsaCtfTool automatically attempts them.
- Trap: // for the division of large integers (never /). Respect the padding when decrypting.
