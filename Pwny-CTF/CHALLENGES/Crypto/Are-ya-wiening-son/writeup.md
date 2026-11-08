---
title: "Are-ya-wiening-son"
ctf: "Pwny-CTF"
category: "crypto"
difficulty: "Not specified"
points: 350
techniques: ["rsa-small-exponent", "rsa-small-modulus", "rsa-wiener"]
tools: ["python"]
keywords: ["Are-ya-wiening-son", "Pwny-CTF", "crypto", "rsa-small-exponent", "rsa-small-modulus", "rsa-wiener", "python", "https", "rsa"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Crypto/Are-ya-wiening-son/notes.md"
---

# Are-ya-wiening-son (Pwny-CTF, crypto)

## Summary
Challenge **Are-ya-wiening-son** from the Pwny-CTF CTF, crypto category. Main technique: rsa-small-exponent. Abnormally large E (of the same order as n) = signal of a small d -> Wiener attack.

## Statement and artefacts
Wow, that public exponent is huge, I wonder if we can [abuse that somehow](https://en.wikipedia.org/wiki/Wiener%27s_attack)?

`n`, `e`, `c`. The description directly points to the Wikipedia article about the **Wiener attack** and insists: “this exponent audience is huge.” A huge `e` (close to `n`) often signals a small `d`.

**Provided files / artifacts:**
- `work/message.txt (text, 889 B)`

## Recognition signals
- If we observe abnormally large e (of the same order as n) = signal of a small d, think of a Wiener attack.

## Resolution method
1. **The reasoning**

RSA: `e·d ≡ 1 (mod phi(n))`, therefore `e·d - k·phi = 1` for an integer `k`. By dividing by `d·phi`: `e/n ≈ e/phi = k/d + (petit)`. When **`d` is small** (`d < n^{1/4}/3`), `k/d` is a **convergent** of the **continued fraction** expansion of `e/n`.

Algorithm:
1. Expand `e/n` as a continued fraction, list its convergents `k/d`.
2. For each candidate: `phi = (e·d - 1)/k` (must be integer).
3. Check `phi`: `p` and `q` are the roots of `x² - (n - phi + 1)x + n = 0`. If the discriminant is a perfect square and the roots are integer → it is the correct `d`.
4. Decrypt `m = c^d mod n`.

Result: `sigpwny{im_wiening_now}`.

## Solve script
Script path: `scripts/solve.py`

## Flag
sigpwny{im_wiening_now}

## Lessons and reusable patterns
- abnormally large e (of the same order as n) = signal of a small d -> Wiener attack.
- Condition: d < (1/3)·n^{1/4}. Beyond that, Boneh-Durfee variant (lattices) up to d < n^{0.292}.
- Key mechanics: convergent continued fractions of e/n -> candidates k/d -> test via the
- Script: work/solve.py.
