---
title: "Add-One"
ctf: "Pwny-CTF"
category: "crypto"
difficulty: "Not specified"
points: 200
techniques: ["aes-cbc", "xor-cipher"]
tools: ["netcat", "python"]
keywords: ["Add-One", "Pwny-CTF", "crypto", "aes-cbc", "xor-cipher", "netcat", "python", "aes", "xor", "cbc"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Crypto/Add-One/notes.md"
---

# Add-One (Pwny-CTF, crypto)

## Summary
Challenge **Add-One** from the Pwny-CTF CTF, crypto category. Main technique: aes-cbc. IV in CBC = direct control (by XOR) of the 1st decrypted block. XORing a pattern in the IV

## Statement and artefacts
Can you add one to an encrypted integer?

`nc chal.sigpwny.com 1987`

The server encrypts a random integer `P` (16 bytes = 1 block) in AES-CBC with random key+IV and gives `IV` and `C`. We must return `(iv', C')` such as `decrypt(C', iv') == P + 1`. Hint: the CBC decipherment diagram, “what happens if we manipulate the IV?” »

**Provided files / artifacts:**

## Recognition signals
Not specified.

## Resolution method
1. **The reasoning**

AES-CBC, 1 block: `C = E_k(P ⊕ IV)` encryption, `decrypt(C, IV) = D_k(C) ⊕ IV` decryption. We don't know the key, but we notice: if we **reuse `C`** and only change the IV,
```
decrypt(C, iv') = D_k(C) ⊕ iv' = P ⊕ (IV ⊕ iv')
```
(because `D_k(C) ⊕ IV = P`). Giving `iv' = IV ⊕ Δ` therefore produces `P ⊕ Δ`. **Changing the IV amounts to XORing the decrypted plaintext** — it's the classic CBC *bit-flipping*.

But we want `P + 1` (**arithmetic** addition), not an XOR. `P ⊕ 1 == P + 1` only if `P` is **even** (low order bit at 0, therefore no carry). `P` is random → ~**50%** chance. The program does not loop, but we can **reconnect**: at each connection `P` is new, so we retry `iv' = IV ⊕ 1` (flip of the last bit) with the same `C` until we come across an even `P`.

```
```

## Solve script
Script path: [scripts/solve.py](scripts/solve.py)

## Flag
sigpwny{if_it_works_sometimes_thats_good_enough}

## Lessons and reusable patterns
- IV in CBC = direct control (by XOR) of the 1st decrypted block. XORing a pattern in the IV
- Attention XOR ≠ arithmetic addition: P ⊕ 1 = P + 1 only without retention (P even). Hence the
- Script: work/solve.py.
