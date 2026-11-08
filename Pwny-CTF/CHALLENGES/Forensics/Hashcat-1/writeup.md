---
title: "Hashcat-1"
ctf: "Pwny-CTF"
category: "forensics"
difficulty: "Not specified"
points: 50
techniques: ["password-cracking", "hash-cracking"]
tools: ["john", "hashcat"]
keywords: ["Hashcat-1", "Pwny-CTF", "forensics", "password-cracking", "hash-cracking", "john", "hashcat", "got"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Forensics/Hashcat-1/notes.md"
---

# Hashcat-1 (Pwny-CTF, forensics)

## Summary
Challenge **Hashcat-1** from the Pwny-CTF CTF, forensics category. Main technique: password-cracking. Hashcat mode 1400 = SHA-256. rockyou = reference wordlist.

## Statement and artefacts
Time to start using wordlists and Hashcat! One of the password hashes for a new RSO I'm starting got leaked. Here's the SHA256 hash:

`c7ac40770bbc66d3b7cab1dcc6e6f6d984f600638565fa003301180014216f45`

**Provided files / artifacts:**
- `hash (file, 64 B)`

## Recognition signals
Not specified.

## Resolution method
1. Provided **SHA-256** hash: `c7ac40770bbc66d3b7cab1dcc6e6f6d984f600638565fa003301180014216f45`.
2. `hashcat -m 1400 hash rockyou.txt` (or `john --format=raw-sha256`) → **`Hateemmaclub1`**.
3. Check: `echo -n "Hateemmaclub1" | sha256sum` = the hash.

## Flag
Hateemmaclub1

## Lessons and reusable patterns
- Hashcat mode 1400 = SHA-256. rockyou = reference wordlist.
