---
title: "ChronoGrind"
ctf: "2026-hiCTF"
category: "crypto"
difficulty: "hard"
points: null
techniques: ["xor-cipher"]
tools: ["gmpy2", "pycryptodome", "python"]
keywords: ["ChronoGrind", "hiCTF", "crypto", "xor-cipher", "gmpy2", "pycryptodome", "python", "zip", "xor", "nonce"]
status: "solved"
has_script: true
source: "hiCTF/Cryptography/ChronoGrind/notes.md"
---

# ChronoGrind (hiCTF, crypto)

## Summary
Challenge **ChronoGrind** from the hiCTF CTF, crypto category. Main technique: xor-cipher. “Patience isn't a virtue here, it's the only exploit... your cores won't save you. Bring a load. » SHA-256 compliant zip.

## Statement and artefacts
“Patience isn't a virtue here, it's the only exploit... your cores won't save you. Bring a load. » SHA-256 compliant zip.

**Provided files / artifacts:**
- `chronogrind.zip (archive, 1.8 KB)`
- `work/checkpoint.txt (text, 628 B)`
- `work/flag.enc (file, 68 B)`
- `work/run.log (text, 4.7 KB)`
- `work/state.dat (file, 1.3 KB)`

## Recognition signals
- Signal: Rivest-Shamir-Wagner time lock puzzle — v = seed^(2^cycles) mod anchor, not parallelizable (each square depends on the previous one).

## Resolution method
1. **Decoding of state.dat**

All the file except `CGD1` is **XORed with 0x4C** (hence the many `L` = 0x00 bytes). After 2 header bytes, **TLV** records: type(1) | length(4, little-endian) | data. The device instructions (in plain text after decoding) give everything:
```
anchor = rec[11] (base 241), seed = rec[22] (base 241), cycles = rec[33] (decimal)
chk    = rec[44] = sha256('anchor:seed:cycles')[:8]
v = seed ; repeat cycles times: v = v*v mod anchor
k = sha256(v on 256 bytes big-endian)
flag.enc = 'CGFX' | ver(1) | nonce(12) | tag(16) | ct   -> ChaCha20-Poly1305
```
Values: **cycles = 9,000,000,000**, anchor ≈ **2048 bits** (safe prime, non-factorizable → no shortcut).

| Stage | Action | Result |
|---|---|---|
| 1 | XOR 0x4C + TLV analysis from offset 6 | anchor/seed/cycles; `chk` validated |
| 2 | Find a shortcut (little postman, Fermat, resume recording) | none — the statement was true |
| 3 | Modulo 2048 bit square speed measurement | loop 1.10 µs; `gmpy2.powmod(v, 2^N, anchor)` **0.72 µs** (same, verified) |
| 4 | Throw the 9×10⁹ squares in the background with darning stitches | ~2 h 40 ; `v` obtained |
| 5 | `k = sha256(v, 256 B big-endian)`; ChaCha20-Poly1305 | valid tag → flag |

## Solve script
Script path: [scripts/solve.py](scripts/solve.py)

## Flag
hiCTF{n1c3_w0rk_n0w_t4k3_s0m3_r3}

## Lessons and reusable patterns
- Recognize: a statement that emphasizes time/patience (“your cores won't save you”) + a large sequential iteration v = v² mod N = time-lock puzzle. The only shortcut would be to factor N (impossible here: safe prime 2048 bits).
- Not parallelizable: each square needs the previous one -> only one core, no GPU/multi-core acceleration.
- gmpy2.powmod(v, 2n, N) does exactly n squares**, in C, faster than a Python loop.
- Essential recovery points for a calculation lasting several hours (container restart, shutdown).
- Always run in background (run_in_background / nohup) and check the Poly1305 tag (no false positives).
