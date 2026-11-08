---
title: "Curveball"
ctf: "Pwny-CTF"
category: "crypto"
difficulty: "Not specified"
points: 350
techniques: ["aes-cbc", "elliptic-curve", "encoding", "wifi"]
tools: ["sage", "python"]
keywords: ["Curveball", "Pwny-CTF", "crypto", "aes-cbc", "elliptic-curve", "encoding", "wifi", "sage", "python", "aes", "ecc", "hex", "got", "cbc", "padding"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Crypto/Curveball/notes.md"
---

# Curveball (Pwny-CTF, crypto)

## Summary
Challenge **Curveball** from the Pwny-CTF CTF, crypto category. Main technique: aes-cbc. In ECC, a point is almost determined by its abscissa alone (only the sign of y remains).

## Statement and artefacts
Hi there Bob! Let's say you wanted to send a handshake to Alice. You choose a curve `y^2 = (x^3 + ax + b) mod p` and generator point `G(G_x, G_y)`.

Now Alice was going to send you her public point Q_a, but it seems that the transmission glitched, and you only got her x coordinate, `Q_a_x`. Can you still get your shared secret?

**Note**: The actual shared secret for the decryptor would be the SHA-256 hash of the x coordinate of the shared secret. So that would be `sha256(S_x)`

**Note**: There are two shared secrets you can arrive at, only one of them will work.

**author**: Sagnik

We are Bob in an ECDH. `y² = x³ + ax + b mod p` curve, `G` generator. Alice was supposed to send her public point `Q_a`, but we only received her **abscissa** `Q_a_x`. We also know Bob's private key `n_B`. Find the shared secret. Notes: there are **two** possible secrets, only one works; the secret for the decryptor is `sha256(S_x)`.

**Provided files / artifacts:**
- `work/client.json (text, 508 B)`

## Recognition signals
Not specified.

## Resolution method
1. **The reasoning**

ECDH: shared secret `S = n_B · Q_a` (Alice's point multiplied by Bob's private key). `y` coordinate is missing from `Q_a`. But the equation of the curve gives `y² = x³ + ax + b mod p`: knowing `x` provides `y` **up to two values** (the two square roots modulo `p`, `+y` and `-y`). There are therefore **two candidate `Q_a` points** → two possible secrets (hence the note “only one walk”).

Method:
1. Calculate `rhs = x³ + ax + b mod p`, take the two square roots (`sqrt_mod`, Tonelli-Shanks).
2. For each `y`, form `Q_a = (x, y)`, calculate `S = n_B · Q_a` (point exponentiation).
3. Derive the key (the `decryptor.py` makes `AES_key = sha1(str(secret))[:16]`), where `secret = sha256(S_x)` (hex). Decrypt in AES-CBC. The correct `y` gives a valid PKCS7 padding → flag.

```
```

## Solve script
Script path: `scripts/decryptor.py`
Script path: `scripts/solve.py`

## Flag
sigpwny{n0t_s0_s3cr3t_anYm0r3}

## Lessons and reusable patterns
- In ECC, a point is almost determined by its abscissa alone (only the sign of y remains).
- Reflex: y = sqrt_mod(x³+ax+b, p) (Tonelli-Shanks), try both roots.
- Read carefully how the key is derived from the secret (here sha256(S_x) then sha1(...)[:16]), format
- Script: work/solve.py (EC arithmetic implemented by hand, no brainer).
