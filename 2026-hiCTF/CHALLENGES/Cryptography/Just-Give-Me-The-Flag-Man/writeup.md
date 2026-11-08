---
title: "Just-Give-Me-The-Flag-Man"
ctf: "2026-hiCTF"
category: "crypto"
difficulty: "medium"
points: null
techniques: ["vigenere", "substitution-cipher", "caesar-cipher", "encoding"]
tools: ["z3", "python"]
keywords: ["Just-Give-Me-The-Flag-Man", "hiCTF", "crypto", "vigenere", "substitution-cipher", "caesar-cipher", "encoding", "z3", "python", "zip", "base64", "hex"]
status: "solved"
has_script: true
source: "hiCTF/Cryptography/Just-Give-Me-The-Flag-Man/notes.md"
---

# Just-Give-Me-The-Flag-Man (hiCTF, crypto)

## Summary
Challenge **Just-Give-Me-The-Flag-Man** from the hiCTF CTF, crypto category. Main technique: vigenere. Stacking of encodings (hex, Ascii85, Base91) and substitutions (Atbash, ROT47, Beaufort); identify each layer with its alphabet

## Statement and artefacts
**Provided files / artifacts:**
- `chall.txt (text, 156 B)`
- `chall.zip (archive, 245 B)`

## Recognition signals
- Signal: stacking of encodings (hex, Ascii85, Base91) and substitutions (Atbash, ROT47, Beaufort); identify each layer with its alphabet.

## Resolution method
1. | Layer | Transformation | Clue that revealed it |
|---|---|---|
| 1 | Hex byte **written backwards** (unit first); letters a-f in **Atbash** (a↔z, b↔y, c↔x, d↔w, e↔v, f↔u) | 2nd character always 2-7 (= most significant ASCII); 1st character ∈ 0-9 + u..z (16 symbols = hex) |
| 2 | String **inverted** → **Ascii85** | Among the 720 letter→a-f correspondences tested, only the “mirrored” ones give a fully printable Ascii85 |
| 3 | **ROT47** → **Base91** | Systematic search ROT-N × inversion × decoders → `feKTH{uf1ht1zg_7fv0sgf_7f3_l4u3u}` |
| 4 | **Beaufort key `m`**: `clear = (12 − ​​encrypted) mod 26` (letters only) | `feKTH` vs `hiCTF`: encrypted + clear = 12 for each letter |

2. Intermediate results:

```
layer 1 : 5G?qS<,gB39?aNcN9#F":,$MEP.^6nb2b3h?3<G,`E&\"GD@T^9,
layer 2 : #!dvnJk6rRHc9"NB7NnI*/1##$!DLYv$^:z3#<Tjw
layer 3 : feKTH{uf1ht1zg_7fv0sgf_7f3_l4u3u}
flag     : hiCTF{sh1ft1ng_7hr0ugh_7h3_b4s3s}
```

## Solve script
Script path: `scripts/solve.py`

## Flag
hiCTF{sh1ft1ng_7hr0ugh_7h3_b4s3s}

## Lessons and reusable patterns
- Recognize a base by its alphabet: 0-9a-f hex;!->u Ascii85; A-Za-z0-9+/= Base64; Base91 = almost all printable ASCII except -, \, ' and space.
- Printable test: good decoding gives printable ASCII; printable but unreadable output = one more layer.
- Known plain text (hiCTF{) to identify a substitution: constant difference -> Caesar/ROT; constant sum -> Beaufort / mirror alphabet; periodic pattern -> Vigenère.
- Missed clue: assuming a simple shift a->u (instead of Atbash) gave a layer 1 that was printable but undecodable; it was the exhaustive test of 720 matches that revealed the mirror.
- Writing a small automatic search for decode strings (depth 4-5, filter "≥ 95% printable") saves a lot of time.
