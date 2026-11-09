---
title: "Cairn"
ctf: "2026-hiCTF"
category: "crypto"
difficulty: "medium"
points: null
techniques: ["elliptic-curve", "hash-collision"]
tools: ["unzip", "python-flint", "pycryptodome", "gcc", "python"]
keywords: ["Cairn", "hiCTF", "crypto", "elliptic-curve", "hash-collision", "unzip", "python-flint", "pycryptodome", "gcc", "python", "zip", "aes", "gcm"]
status: "solved"
has_script: true
source: "hiCTF/Cryptography/Cairn/notes.md"
---

# Cairn (hiCTF, crypto)

## Summary
Challenge **Cairn** from the hiCTF CTF, crypto category. Main technique: elliptic-curve. “One step at a time. Don't look back. » SHA-256 compliant zip.

## Statement and artefacts
- `p = 2^256 − 2^32 − 977` (first of **secp256k1**), `p ≡ 3 mod 4` → GF(p²) = GF(p)[i]/(i²+1).
- Departure `j0 = 1728` (supersingular because p ≡ 3 mod 4) → all roots remain in GF(p²).
- For `i = 0 … T−1` (T = 1,048,576): `h = SHA256(LE32(a)‖LE32(b) ‖ BE8(i) ‖ salt)` → `l = [2,3,5,7][h[0] % 4]` → **distinct** roots of `Phi_l(j, Y)` (part without square), sorted by `(a, b)` → `j = r[h[1] % n]`.
- `key = SHA256(ser(j_T) ‖ "IsogenyLabyrinth")` → AES-256-GCM.
- “Do not look back” / “one step at a time” = **no shortcut**: each step depends on the hash of the previous one, so no jump or parallelization.

**Provided files / artifacts:**
- `cairn.zip (archive, 4.1 KB)`

## Recognition signals
- Signal: random walk in the graph of l-isogenies: the neighbors of j are the roots of Phi_l(j, Y) in GF(p²). You have to replay it exactly and quickly enough (2²⁰ sequential steps).

## Resolution method
1. | Step | Action | Result |
|---|---|---|
| 1 | `sha256sum`, `unzip`, reading `RULES.md` / `challenge.json` | Clear specification: the job is to faithfully replay it |
| 2 | `work/solve.py` (python-flint, `fq_default` + `roots()`) | Reference faithful to the spec, but **16 ms/step → ~4.6 h** |
| 3 | FLINT measurements (`roots`, `pow_mod`, `factor` on GF(p)) | 8 to 30 ms: GF(p²) with a large p goes through the generic, slow representation |
| 4 | Track “twisting points + Vélu” | **Discarded**: 5 divides neither p+1 nor p−1 (E[5] only in GF(p⁸)), a voluntary choice of the author |
| 5 | `work/cairn.c`, dedicated C solver (in the rest of the method) | 1.7ms/step |
| 6 | `./cairn 2000` compared to `solve.py … 2000` | **j identical** → C is validated |
| 7 | `./cairn` (~30 min in background) then `decrypt.py` | GCM tag accepted → flag |

2. **The C solver (work/cairn.c)**

1. **GF(p) on 4 64-bit words**, fast reduction thanks to `2^256 ≡ 2^32 + 977 (mod p)`; GF(p²) in Karatsuba (3 multiplications).
2. **Only one big exponentiation per step**: `H = Y^((p²−1)/42) mod f`. For each root r, H(r) is a **42ᵉ root of unity** (42 = 2·3·7 divides p−1), and these values ​​separate the roots.
3. **Frobenius** to divide the exponent by two: `D = Y^((p−1)/42)`, `Y^p = Y·D⁴²`, and `D^p = Σ conj(dₖ)·(Y^p)^k` (in GF(p²), raise to the power p = conjugate). Then `H = D·D^p`.
4. `G(Z) = ∏(Z − H(r))` via traces + Newton identities → which ζ ∈ μ₄₂ appear → `pgcd(f, H − ζ)` isolates each root. Collisions (class ≥ 2) → Cantor–Zassenhaus emergency.
5. PGCD **without division** (pseudo-remainders: on a field the coefficients do not increase) → a single inversion at the end.

## Solve script
Script path: [scripts/cairn.c](scripts/cairn.c)
Script path: [scripts/decrypt.py](scripts/decrypt.py)
Script path: [scripts/gen.py](scripts/gen.py)
Script path: [scripts/solve.py](scripts/solve.py)

## Flag
hiCTF{w41k_th3_sup3rs1n9u14r_l46yr1ntH}

## Lessons and reusable patterns
- Recognize: j-invariant, modular polynomials Phi_l, GF(p²), j0 = 1728, millions of steps chained by a hash. It's an implementation challenge, not a flaw: crypto is healthy, you just have to calculate.
- Pitfalls of the spec: lexicographic order (a, b), part without square (double roots near j = 1728), LE32 for j and BE8 for i, integers of 70 digits (json Python OK, no floats).
- Winning reflex: slow but faithful version -> compare over N steps -> fast version. Without this comparison, a 1-bit error in step 3 would result in a false j_T with no way of knowing before the GCM tag.
- Long calculation: first measure time per step and extrapolate, then run in background.
- The GCM tag is the final proof (no false positive possible).
