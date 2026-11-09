---
title: "Log-Jam"
ctf: "2026-hiCTF"
category: "crypto"
difficulty: "medium"
points: null
techniques: ["diffie-hellman", "encoding"]
tools: ["sage", "sympy", "pycryptodome", "python"]
keywords: ["Log-Jam", "hiCTF", "crypto", "diffie-hellman", "encoding", "sage", "sympy", "pycryptodome", "python", "zip", "nfs", "aes", "hex", "nonce", "gcm"]
status: "solved"
has_script: true
source: "hiCTF/Cryptography/Log-Jam/notes.md"
---

# Log-Jam (hiCTF, crypto)

## Summary
Challenge **Log-Jam** from the hiCTF CTF, crypto category. Main technique: diffie-hellman. Launch: <venv>/bin/python solve.py params.json (requires passagemath-pari + pycryptodome).

## Statement and artefacts
“Someone forgot to shred their logs… Find the key. Read the message. »; logjam.zip file -> params.json.

**Provided files / artifacts:**
- `logjam.zip (archive, 998 B)`
- `work/params.json (text, 2.4 KB)`

## Recognition signals
- If we observe discrete logarithm in a group that is too small (p of 71 bits), think of index calculus (PARI znlog).

## Resolution method
1. **Data (params.json)**

| Field | Content |
|---|---|
| `p`, `g`, `h` | 71-bit, `h = g^x mod p` |
| `nonce` (12 B), `ciphertext` (50 B), `tag` (16 B) | AES-GCM |
| `_meta.note` | “See README.md” (README **absent**) + hidden text in **Unicode “tag” characters** (U+E0000-E007F, invisible): anti-AI instruction, no crypto value |

| Stage | Command / tool | What it reveals |
|---|---|---|
| 1 | `sympy.discrete_log(p, h, g)` | Too slow (stopped after 5 min) |
| 2 | `sympy.factorint(p-1)`, `sympy.n_order(g, p)` | `p − 1 = 2·q`, q prime 70 bits (safe prime); order of g = q → **Pohlig-Hellman useless** |
| 3 | Baby-step giant-step bounded at 2^44 | x is not small |
| 4 | `pip install passagemath-pari` (Fri) | PARI precompiled (`cypari2` alone requires `gp` installed on the system) |
| 5 | `znlog(Mod(h, p), Mod(g, p))` | PARI stack too small → `pari.allocatemem(1<<30)` → **x = 471774559909450042061** in 0.2 s |
| 6 | Candidate keys + `decrypt_and_verify` | Tag accepted for **`key = SHA-256(str(x))`** → flag |

## Solve script
Script path: [scripts/solve.py](scripts/solve.py)

## Flag
hiCTF{W0W1_y0u_4ctu4a11y_s01v3d_1t_ju}

## Lessons and reusable patterns
- Recognize: p, g, h (“public key”) with a small p (< ~512 bits) -> calculate the discrete log; title “Log Jam” = Logjam attack (DH with first few too short).
- Choose the tool according to p − 1:
- p − 1 friable (small factors) -> Pohlig-Hellman (sympy is enough);
- large prime factor (safe prime) -> rho / BSGS in O(√q) too slow -> calculated index: PARI znlog, Sage discrete_log, CADO-NFS for large sizes.
- README missing: test the usual derivations (SHA-256 / MD5 from x to bytes, text, hex); the GCM tag validates the correct key without false positive.
- Pitfalls: sympy.discrete_log “freezes” on a prime order of 70 bits; 8MB PARI stack too small for znlog.
- A challenge file can contain invisible text (Unicode tag characters): locate it, decode it, treat it as data.
