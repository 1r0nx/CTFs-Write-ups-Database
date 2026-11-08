---
title: "flag_format"
ctf: "Pwny-CTF"
category: "crypto"
difficulty: "Not specified"
points: 100
techniques: ["xor-cipher", "encoding"]
tools: ["cyberchef"]
keywords: ["flag_format", "Pwny-CTF", "crypto", "xor-cipher", "encoding", "cyberchef", "zip", "xor", "hex"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Crypto/flag_format/notes.md"
---

# flag_format (Pwny-CTF, crypto)

## Summary
Challenge **flag_format** from the Pwny-CTF CTF, crypto category. Main technique: xor-cipher. XOR key repeated + start of known clear -> key recovered as soon as known clear ≥ key length. Here the format sigpwny{ (8 char.) = stack the key (8 bytes).

## Statement and artefacts
What's the flag format again?

Can you decrypt the original message given the encrypted output in "message.txt"?

**Provided files / artifacts:**
- `message.txt (text, 70 B)`

## Recognition signals
- Signal: Trap: a known-plaintext attack can give false positives (hit at another offset); keep the one whose text is entirely readable and coherent (sigpwny{.}).
- Signal: Generalization: if the key is longer than the known start, find the key length (Kasiski / IC) then attack each column.

## Resolution method
1. `chal.py`: `xor(flag, key)` with `key` = 8 random bytes, `cycle(key)` (repeated key). `message.txt` = result in hex.
2. Flaw: the flag always starts with `sigpwny{` = **exactly 8 bytes = length of the key**.
3. `K = C ⊕ P`: XOR the first 8 bytes of the cipher with `b"sigpwny{"` → **the whole key**.

```python
   ct = bytes.fromhex(open("message.txt").read().strip())
   key = bytes(c ^ p for c, p in zip(ct[:8], b"sigpwny{"))
   from itertools import cycle
   print(bytes(c ^ k for c, k in zip(ct, cycle(key))))   # sigpwny{now_you_know_the_plaintext}
   ```

4. Decrypt the entire message with the repeated key.

## Discarded approaches
- Tools: CyberChef “From Hex” -> “XOR” (known key) · xortool -c ' ' if key is unknown (finds length + key).

## Flag
sigpwny{now_you_know_the_plaintext}

## Lessons and reusable patterns
- XOR key repeated + start of known clear -> key recovered as soon as known clear ≥ key length. Here the format sigpwny{ (8 char.) = stack the key (8 bytes).
- Trap: a known-plaintext attack can give false positives (hit at another offset); keep the one whose text is entirely readable and coherent (sigpwny{...}).
- Generalization: if the key is longer than the known start, find the key length (Kasiski / IC) then attack each column.
