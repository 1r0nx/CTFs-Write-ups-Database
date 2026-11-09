---
title: "Seal-Trouble-II"
ctf: "Pwny-CTF"
category: "crypto"
difficulty: "Not specified"
points: 200
techniques: ["xor-cipher", "encoding"]
tools: ["python"]
keywords: ["Seal-Trouble-II", "Pwny-CTF", "crypto", "xor-cipher", "encoding", "python", "xor", "hex"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Crypto/Seal-Trouble-II/notes.md"
---

# Seal-Trouble-II (Pwny-CTF, crypto)

## Summary
Challenge **Seal-Trouble-II** from the Pwny-CTF CTF, crypto category. Main technique: xor-cipher. XOR repeated key: if we know the key length L and part of the plaintext, key = ct ^ pt

## Statement and artefacts
The seal has gotten smarter and decided to not hide his passphrase in a photo of himself. However, he forgot what it was.:( He remembers that his passphrase is five characters and is comprised only of lowercase alphabetical letters. Can you help us recover his passphrase and use that to decrypt the message?

**author**: Sophia

The script XORs a message with a repeated passphrase: `ct[i] = msg[i] ^ key[i % len(key)]`. The passphrase is **5 characters, lowercase**. `message.txt` is the cipher (hex) of the real flag.

**Provided files / artifacts:**
- `work/message.txt (text, 68 B)`

## Recognition signals
- Signal: XOR repeated key: if we know the key length L and part of the plaintext, key = ct ^ pt.
- Signal: Otherwise: find L (coincidence index / Kasiski), then frequency analysis column by column.

## Resolution method
1. **The reasoning**

Repeated key XOR + **known key length (5)** + **start of known plaintext** (`sigpwny{`) = immediately breakable by **known-plaintext**: `key[i] = ct[i] ^ pt[i]`. The first 5 bytes of the flag (`sigpw`) directly give the 5 bytes of the key. We check the consistency on the following bytes (`ny{` must return `key[0], key[1], key[2]`), then we decrypt everything:
```
passphrase = "phish"
flag = sigpwny{thank_you_for_the_fish!!!}
```
(Alternative brute force: 26^5 ≈ 11.9 M keys, filter those giving printable plaintext / starting with `sigpwny{`; known-plaintext is instantaneous and avoids that.)

## Solve script
Script path: [scripts/solve.py](scripts/solve.py)

## Flag
sigpwny{thank_you_for_the_fish!!!}

## Lessons and reusable patterns
- XOR repeated key: if we know the key length L and part of the plaintext, key = ct ^ pt
- Otherwise: find L (coincidence index / Kasiski), then frequency analysis column by column.
- Script: work/solve.py.
