---
title: "Vigenère-Visionary"
ctf: "Pwny-CTF"
category: "crypto"
difficulty: "Not specified"
points: 100
techniques: ["vigenere", "caesar-cipher"]
tools: ["cyberchef", "python"]
keywords: ["Vigenère-Visionary", "Pwny-CTF", "crypto", "vigenere", "caesar-cipher", "cyberchef", "python", "https"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Crypto/Vigenère-Visionary/notes.md"
---

# Vigenère-Visionary (Pwny-CTF, crypto)

## Summary
Challenge **Vigenère-Visionary** from the Pwny-CTF CTF, crypto category. Main technique: vigenere. Vigenère = Caesar whose offset changes with each letter (dictated by the cyclic keyword). With the key, it's trivial: invert +K to −K, mod 26.

## Statement and artefacts
I guess some people eventually realized that Caesar cipher really wasn't that secure. You'll have to give them some slack - at the time, it was rare for people to even know how to read. Vigenere cipher (https://en.wikipedia.org/wiki/Vigenère_cipher) is an upgrade, with the same alphabet shifting principle, but instead of a single character key or number, it now consists of a keyword, and cycles through this keyword to shift.

I have provided with you the keyword and the encryption function. Create the decryption function and crack the ciphertext. Once you have the plaintext, the flag is `sigpwny{[plaintext goes here]}`

Note: consider this an introduction to repeated key encryption, where the key is extended to match the plaintext/ciphertext length.

**Provided files / artifacts:**
- `ciphertext (file, 37 B)`
- `key (file, 17 B)`

## Recognition signals
- Signal: Without the key: first find the key length (Kasiski / coincidence index), then break each column as an independent Caesar (frequency analysis).
- If we observe Trap modulo, remember to set % 26 (and +26 if necessary) to avoid negative indices.

## Resolution method
1. Files: `key` = `sigpwnyisthebest`, `ciphertext` = `uikhweuqlaqytxseabzaaogbehyippaowwoa`, `vigenere.py` (encryption provided, decryption to write).
2. Encryption formula: `C = (P + K) mod 26` with `P`, `K` = positions 0–25 of plain letter and key letter (key extended by `i % len(key)`).
3. Decryption = **subtract** the offset: `P = (C − K) mod 26`.

```python
   pt = "".join(chr((ord(ct[i]) - ord(k[i%len(k)])) % 26 + ord("a")) for i in range(len(ct)))
   ```

4. Clear = `caesarwithjustalittlebitmoreoliveoil` → flag `sigpwny{...}`.

## Discarded approaches
- Tools: dcode.fr “Vigenere Cipher” (known key mode, or keyless self-breaking) · CyberChef “Vigenère Decode”.

## Solve script
Script path: [scripts/vigenere.py](scripts/vigenere.py)

## Flag
sigpwny{caesarwithjustalittlebitmoreoliveoil}

## Lessons and reusable patterns
- Vigenère = Caesar whose offset changes with each letter (dictated by the cyclic keyword). With the key, it's trivial: invert +K to −K, mod 26.
- Without the key: first find the key length (Kasiski / index of coincidence), then break each column as an independent Caesar cipher (frequency analysis).
- Modulo trap: set % 26 (and +26 if necessary) to avoid negative indices.
