---
title: "Secret-Sauce"
ctf: "Pwny-CTF"
category: "crypto"
difficulty: "Not specified"
points: 550
techniques: ["aes-ecb", "xor-cipher"]
tools: ["python"]
keywords: ["Secret-Sauce", "Pwny-CTF", "crypto", "aes-ecb", "xor-cipher", "python", "aes", "xor", "ecb"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Crypto/Secret-Sauce/notes.md"
---

# Secret-Sauce (Pwny-CTF, crypto)

## Summary
Challenge **Secret-Sauce** from the Pwny-CTF CTF, crypto category. Main technique: aes-ecb. The non-linearity of AES comes only from the S-box. Replace it with an affine function

## Statement and artefacts
He's utilizing his own saucebox for the recipe? And you're laughing at him for that??? LET. HIM. COOK!

A “homemade” AES (fork of AES-Python) with a **modified S-box** (`sauceBox`, given in `chal.txt`), “improved so as not to leak the sauce”. We have the ciphertext (ECB) and we know that the plaintext is `"Secret Sauce: " + flag`.

**Provided files / artifacts:**
- `work/chal.txt (text, 1.5 KB)`

## Recognition signals
- If we observe Looking at the sauceBox, think of sauceBox[i] == i ^ 0xCE for all i.
- Signal: It is therefore no longer the real S-box (non-linear), but a simple XOR by a constant = an affine transformation.
- Signal: However in AES, SubBytes is the only non-linear step.
- Signal: ShiftRows, MixColumns, AddRoundKey are all linear/affine on GF(2).
- If SubBytes becomes affine, **the entire encryption becomes affine**.
- Signal: where M is a fixed linear map (independent of the key) and b depends on the key.

## Resolution method
1. Instantiate the “homemade” AES with the sauceBox and **any key** (e.g. all zero): as `E` is affine, `M(x) = enc(x) ⊕ enc(0)` is linear and independent of the key.
2. Construct the 128×128 matrix of `M` on GF(2) via `M(e_bit)`, invert it (Gaussian elimination).
3. For each block `ci`: `pi = p0 ⊕ M⁻¹(c0 ⊕ ci)`.

The 1st reconstructed block restores `"Secret Sauce: "` (validation), the rest = the flag: `sigpwny{a3s_w1thOut_s4UC3b0x_b3_l1k3__...}`.

1. **The reasoning (the “flaw” = the sauceBox)**

Looking at the `sauceBox`: `sauceBox[i] == i ^ 0xCE` for **all** `i`. It is therefore no longer the real (non-linear) S-box, but a simple **XOR by a constant** = an **affine** transformation.

But in AES, **`SubBytes` is the only non-linear step**. `ShiftRows`, `MixColumns`, `AddRoundKey` are all **linear/affine** on GF(2). If `SubBytes` becomes affine, **the entire cipher becomes affine**:
```
E_k(p) = M(p) ⊕ b(k)
```
where `M` is a **fixed linear** map (key independent) and `b` is key dependent.

**Consequence**: for two blocks encrypted with the same key (ECB mode),
```
c0 ⊕ ci = M(p0) ⊕ M(pi) = M(p0 ⊕ pi)   ⟹   pi = p0 ⊕ M⁻¹(c0 ⊕ ci)
```
**No need for the key!** We know `p0 = "Secret Sauce: "` (1st block) and all `ci`.

## Solve script
Script path: [scripts/aes.py](scripts/aes.py)
Script path: [scripts/solve.py](scripts/solve.py)

## Flag
sigpwny{a3s_w1thOut_s4UC3b0x_b3_l1k3__4f605d23b07ed32388bbe5fe4202281ce2db154394a6b5cdd4270468c8bbced0}

## Lessons and reusable patterns
- The non-linearity of AES comes only from the S-box. Replace it with an affine function
- Reflex: in front of a custom S-box, test if it is affine (sbox[i] == i ^ c, or more
- Script: work/solve.py (imports the aes.py from the challenge).
