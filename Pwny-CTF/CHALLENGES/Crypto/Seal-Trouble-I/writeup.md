---
title: "Seal-Trouble-I"
ctf: "Pwny-CTF"
category: "crypto"
difficulty: "Not specified"
points: 150
techniques: ["xor-cipher", "exif-metadata", "encoding"]
tools: ["exiftool", "cyberchef"]
keywords: ["Seal-Trouble-I", "Pwny-CTF", "crypto", "xor-cipher", "exif-metadata", "encoding", "exiftool", "cyberchef", "png", "exif", "xor", "hex"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Crypto/Seal-Trouble-I/notes.md"
---

# Seal-Trouble-I (Pwny-CTF, crypto)

## Summary
Challenge **Seal-Trouble-I** from the Pwny-CTF CTF, crypto category. Main technique: xor-cipher. "XOR + an image/an annex file" -> search for the key in the metadata (exiftool), not guess it.

## Statement and artefacts
Breaking news: Seals have reached a new level of intelligence and can now create their own XOR encryptions. One left a comment on a photo of themselves. Can you use that to discover the flag?

**author**: Sophia

**Provided files / artifacts:**
- `message.txt (text, 46 B)`
- `seal1.png (image, 1.4 MB)`

## Recognition signals
- Signal: XOR repeated key: if the key is known, direct decryption; otherwise known-plaintext (cf. flag_format) or xortool.

## Resolution method
1. `chal.py`: `encrypt = b ^ key[i % len(key)]`, `key = ord(char) of the passphrase` → Repeated key XOR.
2. `message.txt` = ciphertext hex `1e06...0810` (23 bytes).
3. Clues: the passphrase is in the **photo** → `exiftool seal1.png` reveals `Comment: morefishplz`.
4. Decipher: `plaintext = ciphertext ⊕ (repeated key)` → `sigpwny{seals_like_x0r}`.

## Discarded approaches
- Tools: CyberChef “From Hex” -> “XOR” (UTF8 key morefishplz).

## Flag
sigpwny{seals_like_x0r}

## Lessons and reusable patterns
- "XOR + an image/an annex file" -> search for the key in the metadata (exiftool), not guess it.
- XOR repeated key: if the key is known, direct decryption; otherwise known-plaintext (cf. flag_format) or xortool.
