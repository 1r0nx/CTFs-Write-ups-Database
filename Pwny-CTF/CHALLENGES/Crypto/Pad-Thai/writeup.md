---
title: "Pad-Thai"
ctf: "Pwny-CTF"
category: "crypto"
difficulty: "Not specified"
points: 500
techniques: ["rsa-small-exponent", "rsa-small-modulus", "rsa-padding-oracle", "prng-prediction"]
tools: ["sage", "python"]
keywords: ["Pad-Thai", "Pwny-CTF", "crypto", "rsa-small-exponent", "rsa-small-modulus", "rsa-padding-oracle", "prng-prediction", "sage", "python", "rsa", "coppersmith", "padding"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Crypto/Pad-Thai/notes.md"
---

# Pad-Thai (Pwny-CTF, crypto)

## Summary
Challenge **Pad-Thai** from the Pwny-CTF CTF, crypto category. Main technique: rsa-small-exponent. Deterministic/known padding + small e = Coppersmith (stereotyped message). The flag is the small

## Statement and artefacts
People have told me that you need to use padding with RSA, so I encrypted the flag with my own padding - there shouldn't be a way for you to get it now!

“I was told you need padding with RSA, so I did my own. » Encryption:
```python
msg = b'\x01' * (512 - len(flag)) + flag      # padding = 0x01 repeat
ct  = pow(bytes_to_long(msg), 3, N)            # e = 3, N = p*q (2048 bits each)
```
We have `N` and `ct`.

**Provided files / artifacts:**
- `work/output.txt (text, 2.4 KB)`

## Recognition signals
Not specified.

## Resolution method
1. **The reasoning**

The padding is **constant and known** (only `0x01`). By setting `L = len(flag)`:
```
m = A + x ,  A = int(b'\x01'*(512-L)) · 256^L  (connu) ,  x = int(flag) < 256^L
ct = m^3 mod N  ⟹  f(x) = (A + x)^3 - ct ≡ 0 (mod N)
```
`x` (the flag) is **small** in front of `N`. **Coppersmith's attack** (via Howgrave-Graham + LLL) finds the roots `x0` of `f` modulo `N` as `|x0| < N^{1/deg} = N^{1/3}`. `N` is ~4096 bits → `N^{1/3}` ≈ 1365 bits ≈ 170 bytes, much more than the flag. A network of **dimension 4** (parameter `m=1`) is sufficient.

Method:
1. For each candidate length `L` (unknown → raw), form `f(x) = (A+x)^3 - ct`: coefficients `[(A^3-ct) mod N, 3A^2 mod N, 3A mod N, 1]`.
2. Construct the Coppersmith network `{N·x^0, N·x^1, N·x^2, f(x)}` (scaled by `X=256^L`), reduce it by **LLL**, extract the short polynomial `g`, find its **entire** roots.
3. Check `pow(A+x, 3, N) == ct`. Found at `L = 32`:
```
```

## Solve script
Script path: `scripts/coppersmith.py`
Script path: `scripts/solve.py`

## Flag
sigpwny{b3_c4r3ful_w1th_p4dd1n6}

## Lessons and reusable patterns
- Deterministic/known padding + small e = Coppersmith (stereotyped message). The flag is the small
- Real RSA padding (random OAEP / PKCS#1 v1.5) makes m unpredictable and blocks that; a padding
- Sans sage/fpylll: I implemented an integer LLL (Cohen 2.6.7) pure Python (coppersmith.py),
- Recognize: RSA e=3 (or small) + message with known structure (fixed prefix/suffix) + only one
- Scripts: work/solve.py (+work/coppersmith.py).
