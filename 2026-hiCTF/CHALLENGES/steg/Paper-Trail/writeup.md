---
title: "Paper-Trail"
ctf: "2026-hiCTF"
category: "stego"
difficulty: "hard"
points: null
techniques: ["aes-cbc", "xor-cipher"]
tools: ["unzip", "wayback-machine", "python"]
keywords: ["Paper-Trail", "hiCTF", "stego", "aes-cbc", "xor-cipher", "unzip", "wayback-machine", "python", "zip", "aes", "xor", "cbc", "padding"]
status: "solved"
has_script: true
source: "hiCTF/steg/Paper-Trail/notes.md"
---

# Paper-Trail (hiCTF, stego)

## Summary
Challenge **Paper-Trail** from the hiCTF CTF, stego category. Main technique: aes-cbc. Render mode 3 (3 Tr) + empty strings () + data in TJ kerning numbers:

## Statement and artefacts
**Provided files / artifacts:**
- `chall.pdf (document, 503.9 KB)`
- `chall_-000.png (image, 212.7 KB)`
- `chall_-001.png (image, 72.9 KB)`
- `chall_-002.png (image, 23.6 KB)`
- `chall_-003.png (image, 231 B)`
- `chall_-004.png (image, 2.1 KB)`
- `chall_-005.png (image, 127 B)`
- `paper-trail.zip (archive, 465.3 KB)`
- `unveil.txt (text, 55.3 KB)`

## Recognition signals
- When a blob looks random after all the "additive/XOR" decoding, think encrypted.

## Resolution method
1. **Established**

| Verification | Result |
|---|---|
| `grep -a -c '%%EOF' chall.pdf` | **only 1** → no incremental update (no old revision in the file) |
| zip (`unzip -z`, `zipinfo -v`, PK signatures) | Clean, PDF identical to local |
| Metadata Info / XMP, trailer `/ID` | Nothing unusual |
| xref vs actual object positions | Consistent; objects 25 and 71 = orphan `/Pages` nodes (point to the same pages, a priori of no interest) |
| ToUnicode (obj 36, 41, 46, 51, 79), `/Alt`, `/ActualText`, JS, attachments | Normal/absent |
| Images (JDFSL, Embry-Riddle/Purdue, CC logos) | Normal |

2. **Next track (not done, to be validated by me)**

“*archived copy*” → retrieve the **original article** (commons.erau.edu / Wayback Machine) and **compare** the content streams: the original streams may also have been modified (kerning), which would give the data or key.

3. **✅ SOLUTION (solved on 2026-11-01) — hiCTF{n3w_ar34_fOr_hid!ng_d4t4_n4m3d_TJ}**

The "encrypted numbers, need external info" lead was the right one: the ~64 "random" bytes of the long lines (stream 179/180/181) are an **AES ciphertext**, and the key/IV were in the **PDF trailer** (table `/ID`), not in the original article.

4. **Payload (64 bytes)**

In each stream 179/180/181, the long line `TJ` carries, after the prefix `() a () b ()`, a sequence of bytes 0-255. Concatenated in page order (179→180→181; 182 only has kerning):
```
ae045988164c448a8e560c5292da7f1722a9c9018e15cb606e10ebb2a27c5944
189f3d75269e3abc0167fa87efa9fe08b0eb74433b0c82d8b5d7f4d5b02139f6   (64 B)
```

5. **Decryption**

- `/ID[0]` = `e3b51a3ba231502d79c55593eb522037` → **AES-128 key**
- `/ID[1]` = `6749db1175e3e659a640695dcc830c82` → **IV**
- `AES-128-CBC(key=/ID[0], iv=/ID[1]).decrypt(blob)` → `b'CTF1\x00(' + "hiCTF{n3w_ar34_fOr_hid!ng_d4t4_n4m3d_TJ}" + padding`
- Container: magic `CTF1`, byte `0x00`, length `0x28` (=40), then the flag of 40 bytes.

## Discarded approaches
- 3 Tr = made invisible; font size 1; empty strings -> the info is in the 169 numbers (20 lines).
- Short lines: values in [-77, 80]. One long line per stream 179/180/181: 2-3 small values ​​then ~21 values ​​in [0, 255] (≈ 64 bytes in total). Flow 182: only short lines.
- Line lengths: 179 = 5,4,8,23,5.7 · 180 = 7,4,7,23,4.6 · 181 = 8,8,24.5 · 182 = 6,4,6.5.

## Solve script
Script path: `scripts/solve.py`

## Flag
hiCTF{n3w_ar34_fOr_hid!ng_d4t4_n4m3d_TJ}

## Lessons and reusable patterns
- Render mode 3 (3 Tr) + empty strings () + data in TJ kerning numbers:
- When a blob looks random after all the “additive/XOR” decoding, think encrypted:
- False leads checked: /Prev 4 0 R = bookmark pointer (Outlines), not a revision;
- Solve script: work/solve.py.
