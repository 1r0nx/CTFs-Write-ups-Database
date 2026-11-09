---
title: "Hashcat-2"
ctf: "Pwny-CTF"
category: "forensics"
difficulty: "Not specified"
points: 250
techniques: ["password-cracking", "hash-cracking"]
tools: ["hashcat", "python"]
keywords: ["Hashcat-2", "Pwny-CTF", "forensics", "password-cracking", "hash-cracking", "hashcat", "python"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Forensics/Hashcat-2/notes.md"
---

# Hashcat-2 (Pwny-CTF, forensics)

## Summary
Challenge **Hashcat-2** from the Pwny-CTF CTF, forensics category. Main technique: password-cracking. Brute force is only realistic if the space is small. Here: nb_pseudos × 10000 tests only, because the format is known -> instantaneous.

## Statement and artefacts
Oh no! Discord's automod is malfunctioning and wasn't able to properly ban a user for violating our code of conduct.

For some reason, it also wasn't able to properly log the username, but it did log the SHA512 hash of their username: `279c061469df1eeec079f3d469bf79ade48f79ef6a5613c42715f0facb2fa618652c1762b05c2df3fd162a770f91e72bb9e7ee5eec4296aedb28dcd061edb112`

Unfortunately, the discriminator (hashtag and the unique 4-digit identifier) at the end of each username (`#0000`) aren't in the list of users we have stored, but the hash does include it. Can you figure out who the violator was?

File: sigpwny_users.txt

Note: Discord uses format `username#dddd`, where `d` is a digit `[0-9]`.

**Author**: Minh

**Provided files / artifacts:**
- `sigpwny_users.txt (text, 1.5 KB)`

## Recognition signals
- Signal: A brute force is only realistic if the space is small. Here: nb_pseudos × 10000 tests only, because the format is known -> instantaneous.

## Resolution method
1. We have a target **SHA-512** hash and a list of nicknames (`sigpwny_users.txt`).
2. The password follows the pattern `pseudo#XXXX` where `XXXX` = 4 digits (0000 → 9999).
3. `solve.py` script: for each nickname, test the 10,000 combinations `pseudo#0000`..`pseudo#9999`, calculate the SHA-512 and compare to the target → found `WhiteHoodHacker#8390`.

## Solve script
Script path: [scripts/solve.py](scripts/solve.py)

## Flag
WhiteHoodHacker#8390

## Lessons and reusable patterns
- Brute force is only realistic if the space is small. Here: nb_pseudos × 10000 tests only, because the format is known -> instantaneous.
- Recognize this type: you are given a hash and a strong constraint on the form of the password (mask). This is exactly what hashcat does in mask mode (-a 3), here reproduced in Python.
- SHA-512 = one-way cryptographic hash function producing 128 hexadecimal (512-bit) characters. We do not “decrypt” a hash: we guess the entry and we re-hash to compare.
- Harder variant: wider mask (letters + numbers + symbols) -> go through hashcat with a real?d?d?d?d mask, or a rule, for GPU speed.
