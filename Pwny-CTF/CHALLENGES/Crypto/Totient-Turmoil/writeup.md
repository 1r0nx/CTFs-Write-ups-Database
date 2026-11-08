---
title: "Totient-Turmoil"
ctf: "Pwny-CTF"
category: "crypto"
difficulty: "Not specified"
points: 150
techniques: ["rsa-small-exponent", "rsa-small-modulus", "encoding"]
tools: ["curl", "yafu", "factordb", "sympy", "pycryptodome"]
keywords: ["Totient-Turmoil", "Pwny-CTF", "crypto", "rsa-small-exponent", "rsa-small-modulus", "encoding", "curl", "yafu", "factordb", "sympy", "pycryptodome", "http", "https", "rsa", "hex", "padding"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Crypto/Totient-Turmoil/notes.md"
---

# Totient-Turmoil (Pwny-CTF, crypto)

## Summary
Challenge **Totient-Turmoil** from the Pwny-CTF CTF, crypto category. Main technique: rsa-small-exponent. Small N (≤ ~256-512 bits) -> factor directly (sympy / factordb / yafu). This is THE most common RSA vulnerability in CTF.

## Statement and artefacts
You've intercepted Alice and Bob's message, can you crack their public key and find the flag? (https://simple.wikipedia.org/wiki/RSA_algorithm)

**Provided files / artifacts:**
- `info.txt (text, 1.7 KB)`
- `message.txt (text, 92 B)`

## Recognition signals
- Signal: message.txt contains n, e=17, and sigpwny{8e6fc3ae41b628ff0e4a357354bbc52f}.
- Signal: This string looks like the flag -> LURE: hex 8e6f.52f is the ciphertext c.
- Signal: It must be deciphered.

## Resolution method
1. `n` is ~128 bits → **factorizable** (n "too small", hence the name). `sympy.factorint(n)` → p, q (~64 bits each).
2. `d = e^-1 mod (p-1)(q-1)`.
3. `m = c^d mod n` with `c = int("8e6f...52f", 16)`.
4. `long_to_bytes(m)` = `n_too_small` → flag `sigpwny{n_too_small}`.

1. **Trap**

`message.txt` contains `n`, `e=17`, and `sigpwny{8e6fc3ae41b628ff0e4a357354bbc52f}`. This string looks like the flag → LURE: the hex `8e6f...52f` is the **ciphertext c**. It must be deciphered.

## Discarded approaches
- Tools: factordb.com, RsaCtfTool -n <n> -e 17 --uncipher <c> (here raw RSA is suitable, no padding), yafu (factorization).

## Flag
sigpwny{n_too_small}

## Lessons and reusable patterns
- n small (≤ ~256-512 bits) -> factor directly (sympy / factordb / yafu). This is THE most common RSA vulnerability in CTF.
- Distrust: a sigpwny{<hex>} in an RSA challenge can be the ciphertext, not the flag. The real flag is the deciphered plaintext.
