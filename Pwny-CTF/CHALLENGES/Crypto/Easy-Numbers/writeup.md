---
title: "Easy-Numbers"
ctf: "Pwny-CTF"
category: "crypto"
difficulty: "easy"
points: 250
techniques: ["rsa-small-exponent", "rsa-broadcast"]
tools: ["sage", "sympy", "python"]
keywords: ["Easy-Numbers", "Pwny-CTF", "crypto", "rsa-small-exponent", "rsa-broadcast", "sage", "sympy", "python", "rsa", "padding"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Crypto/Easy-Numbers/notes.md"
---

# Easy-Numbers (Pwny-CTF, crypto)

## Summary
Challenge **Easy-Numbers** from the Pwny-CTF CTF, crypto category. Main technique: rsa-small-exponent. Same m, same small e, several N, no padding -> Håstad: CRT then e-th root.

## Statement and artefacts
Number Theory is an important part of any crypto challenge. Here's an easy one using the Chinese Remainder Theorem.

The same flag is encrypted for 4 friends, each with their RSA key: same `e = 13`, different `N` modules. We have the 4 couples `(N_i, ct_i)`. Hint: “solvable in < 5 lines with sage” + “CRT”.

**Provided files / artifacts:**
- `work/easy-numbers.txt (text, 2.8 KB)`

## Recognition signals
Not specified.

## Resolution method
1. **The reasoning**

RSA without padding: `ct_i = m^e mod N_i` with `e = 13` identical everywhere, `m` identical (the flag).
- **CRT** (Chinese remainder theorem): from the congruences `X ≡ ct_i (mod N_i)`, we reconstruct the unique `X = m^13 mod (N_1·N_2·N_3·N_4)`.
- As the flag is **short**, `m^13 < N_1·N_2·N_3·N_4` (4 modules ~1024 bits → produces ~4096 bits; `m` ~250 bits → `m^13` ~3300 bits). So the modular reduction did **not** take place: `X` **is** exactly `m^13` (in full).
- Just take the **entire 13th root** of `X` → `m` → flag.

Number of ciphers required: you need at least `e` messages if `m` is full size, but here `m` small is enough with only 4 (because `m^13` already fits in the product of 4 modules).

```
X = crt([N_i], [ct_i])        # m^13 mod prod
m = integer_nthroot(X, 13)    # exact root -> sigpwny{numbers_are_fun}
```

## Solve script
Script path: [scripts/solve.py](scripts/solve.py)

## Flag
sigpwny{numbers_are_fun}

## Lessons and reusable patterns
- Same m, same small e, several N, no padding -> Håstad: CRT then e-th root.
- Close variant: a single encrypted with small e and m^e < N -> simple e-th root (no need for CRT).
- Tools: sympy.ntheory.modular.crt, sympy.integer_nthroot (exact integer root + boolean).
- Script: work/solve.py.
