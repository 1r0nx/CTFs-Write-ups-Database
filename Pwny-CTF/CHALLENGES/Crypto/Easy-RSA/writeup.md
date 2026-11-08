---
title: "Easy-RSA"
ctf: "Pwny-CTF"
category: "crypto"
difficulty: "easy"
points: 200
techniques: ["rsa-small-exponent", "rsa-small-modulus", "rsa-padding-oracle"]
tools: ["yafu", "factordb", "sympy", "pycryptodome"]
keywords: ["Easy-RSA", "Pwny-CTF", "crypto", "rsa-small-exponent", "rsa-small-modulus", "rsa-padding-oracle", "yafu", "factordb", "sympy", "pycryptodome", "rsa", "padding"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Crypto/Easy-RSA/notes.md"
---

# Easy-RSA (Pwny-CTF, crypto)

## Summary
Challenge **Easy-RSA** from the Pwny-CTF CTF, crypto category. Main technique: rsa-small-exponent. N small -> factor (same refrain as Totient Turmoil). The comment “n is very small” is an admission.

## Statement and artefacts
RSA (reminder). We give you n and e — can you decipher c? author: Sophia

## Recognition signals
- If the deciphered plaintext starts with \x02. \x00, it's PKCS#1 v1.5: remove the padding (m[m.index(b"\x00")+1:]) or use PKCS1_v1_5.decrypt with the reconstructed key.

## Resolution method
1. `chal.py`: `e=65539`, `n` ~132 bits (comment "n is very small"), `c` = **list of 3 blocks** of bytes (the flag cut).
2. `n` small → `sympy.factorint(n)` → p, q (~66 bits each).
3. `d = e^-1 mod (p-1)(q-1)`.
4. For each block: `m = c^d mod n` (`bytes_to_long` / `long_to_bytes`). The clear one is **padded PKCS#1 v1.5** (`\x02 <random> \x00 <message>`) → take what follows the first `\x00`.
5. Concatenate the 3 pieces → `sigpwny{rsA_FtW:P}`.

## Discarded approaches
- Tools: factordb.com / yafu to factor n; PKCS1_v1_5.decrypt with RSA.construct((n, e, d, p, q)).

## Flag
sigpwny{rsA_FtW:P}

## Lessons and reusable patterns
- n small -> factor (same refrain as Totient Turmoil). The comment “n is very small” is an admission.
- If the decrypted plaintext begins with \x02... \x00, it is PKCS#1 v1.5: remove the padding (m[m.index(b"\x00")+1:]) or use PKCS1_v1_5.decrypt with the reconstructed key.
- Message split into several RSA blocks -> decrypt each one and concatenate.
