---
title: "Not-so-Easy-ECC"
ctf: "Pwny-CTF"
category: "crypto"
difficulty: "easy"
points: 500
techniques: ["elliptic-curve"]
tools: ["netcat", "sage", "python"]
keywords: ["Not-so-Easy-ECC", "Pwny-CTF", "crypto", "elliptic-curve", "netcat", "sage", "python", "ecc"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Crypto/Not-so-Easy-ECC/notes.md"
---

# Not-so-Easy-ECC (Pwny-CTF, crypto)

## Summary
Challenge **Not-so-Easy-ECC** from the Pwny-CTF CTF, crypto category. Main technique: elliptic-curve. “You choose the curve” = trap: make it unique. Discriminant 4a³ + 27b² = 0 -> curve

## Statement and artefacts
I just learned about this cool new encryption scheme called Elliptic Curve Cryptography. It's so powerful, it doesn't matter how I use it!

`nc chal.sigpwny.com 1990`

**author**: Hassam

The server lets us choose `p` (first 128 bits), `a`, `b` from `y² = x³ + a·x + b (mod p)`, draws a point `P` and an integer `k`, gives us `P` and `k·P`, and asks for `k` (discrete logarithm problem on curve elliptical, **ECDLP**). Hint: “you control the parameters of the curve, to be exploited”.

**Provided files / artifacts:**

## Recognition signals
- Signal: “You choose the curve” = trap: make it unique. Discriminant 4a³ + 27b² = 0 -> curve.
- Signal: Other abuses when controlling the curve: smooth order -> Pohlig-Hellman; abnormal curve.

## Resolution method
1. **The reasoning**

ECDLP is hard **only on a well-chosen curve** (non-singular, first order). As we choose the curve, we make it **singular**: with `a = b = 0` we have `y² = x³`, a curve with **cusp** (cusp point) at `(0,0)`. Its group of non-singular points is **isomorphic to the additive group** `(F_p, +)` via the map:
```
t = x/y (and O ↦ 0)
```
The addition of points corresponds to the addition of `t`. So `k·P ↦ k·t_P`, and:
```
k = t_{kP} · t_P⁻¹  mod p
```
A simple modular calculation, no hard discrete log. (For a singularity with **node** `y²=x³+ax²`, the group would be isomorphic to `F_p^*` → multiplicative discrete log, also easy if smooth.)

```
```

## Solve script
Script path: [scripts/mini_ecdsa.py](scripts/mini_ecdsa.py)
Script path: [scripts/solve.py](scripts/solve.py)
Script path: [scripts/tonelli_shanks.py](scripts/tonelli_shanks.py)

## Flag
sigpwny{okay_next_time_ill_make_the_curve}

## Lessons and reusable patterns
- “You choose the curve” = trap: make it unique. Discriminant 4a³ + 27b² = 0 -> curve
- Other abuses when controlling the curve: smooth order -> Pohlig-Hellman; abnormal curve
- Script: work/solve.py (t=x/y map, no sage required).
