---
title: "Odd-One-Out"
ctf: "Pwny-CTF"
category: "crypto"
difficulty: "Not specified"
points: 200
techniques: ["aes-ecb", "encoding"]
tools: ["python"]
keywords: ["Odd-One-Out", "Pwny-CTF", "crypto", "aes-ecb", "encoding", "python", "https", "aes", "hex", "cbc", "ecb", "ctr"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Crypto/Odd-One-Out/notes.md"
---

# Odd-One-Out (Pwny-CTF, crypto)

## Summary
Challenge **Odd-One-Out** from the Pwny-CTF CTF, crypto category. Main technique: aes-ecb. Recognize AES-ECB: encrypted multiple of 16 bytes + blocks of 16 repeated bytes. Reflex

## Statement and artefacts
This challenge is taken from the website https://cryptopals.com/sets/1/challenges/8 which is the source of a lot of AES challenges itself. I downloaded the list of ciphertexts to make it a bit easier. There's exactly one ciphertext that has been encoded with AES ECB. Find this ct. Flag is the correct hex ciphertext contained within chal.txt that meets the condition

A `chal.txt` file contains 204 encrypted in hex. Exactly **one** was encrypted in **AES-ECB**. We have to find him. The flag is this hexa cipher (cryptopals set 1, challenge 8).

**Provided files / artifacts:**
- `work/chal.txt (text, 63.9 KB)`

## Recognition signals
- Signal: Format trap: the description says “the flag IS the hex” -> submit as is (or wrapped.

## Resolution method
1. **The reasoning**

AES encrypts in blocks of **16 bytes**. **ECB** (Electronic CodeBook) mode encrypts each block **independently** with the same key, without chaining or IV: `C_i = E_k(P_i)`. Direct consequence:
> two **identical** plaintext blocks produce two **identical** ciphertext blocks.

This is THE weakness of the ECB (see the famous “Tux penguin” which remains visible encrypted in ECB). So if a plaintext contains aligned repetitions of 16 bytes, its ECB cipher will have **duplicated blocks of 16 bytes**. The other modes (CBC, CTR, etc.) hide these repetitions.

For each line: cut the cipher into blocks of 16 bytes, and locate the line where `len(blocks)!= len(set(blocks))` (there are duplicates). Only one line matches. Here the `08649af70dc06f4fd5d2d69c744cd283` block appears **4 times**.

Response (ECB encrypted):
```
d880619740a8a19b7840a8a31c810a3d08649af70dc06f4fd5d2d69c744cd283...744cd283...744cd283...744cd283...
```
(see `work/solve.py` for full line)

## Solve script
Script path: `scripts/solve.py`

## Flag
d880619740a8a19b7840a8a31c810a3d08649af70dc06f4fd5d2d69c744cd283e2dd052f6b641dbf9d11b0348542bb5708649af70dc06f4fd5d2d69c744cd2839475c9dfdbc1d46597949d9c7e82bf5a08649af70dc06f4fd5d2d69c744cd28397a93eab8d6aecd566489154789a6b0308649af70dc06f4fd5d2d69c744cd283d403180c98c8f6db1f2a3f9c4040deb0ab51b29933f2c123c58386b06fba186a

## Lessons and reusable patterns
- Recognize AES-ECB: encrypted multiple of 16 bytes + blocks of 16 repeated bytes. Reflex
- ECB = no IV, deterministic, avoids plaintext structure. To be banned in practice.
- Format trap: the description says “the flag IS the hex” -> submit as is (or wrapped
- Script: work/solve.py.
