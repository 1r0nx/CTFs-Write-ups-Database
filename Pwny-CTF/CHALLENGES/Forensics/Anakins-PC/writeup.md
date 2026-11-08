---
title: "Anakins-PC"
ctf: "Pwny-CTF"
category: "forensics"
difficulty: "Not specified"
points: 50
techniques: ["password-cracking", "hash-cracking"]
tools: ["hashcat"]
keywords: ["Anakins-PC", "Pwny-CTF", "forensics", "password-cracking", "hash-cracking", "hashcat"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Forensics/Anakins-PC/notes.md"
---

# Anakins-PC (Pwny-CTF, forensics)

## Summary
Challenge **Anakins-PC** from the Pwny-CTF CTF, forensics category. Main technique: password-cracking. Echo -n (without the final \n) is crucial for a correct hash.

## Statement and artefacts
I stole the file `my_private_passwords.txt` from Anakin's PC. The contents are:

```
Hackerman123
idocryptoforfun
iamamathmajor
ihavelonghair
ilikegreenkitkat
ihatediffeq
```

I also stole an MD5 password hash from his computer: `24426f6211bd68ce7647ebfd7f694b42`

Which one of his passwords is he using?

## Recognition signals
Not specified.

## Resolution method
1. We have a list of 6 passwords + an MD5 hash: `24426f6211bd68ce7647ebfd7f694b42`.
2. Hash each candidate and compare: `echo -n "<password>" | md5sum`.
3. `md5(ilikegreenkitkat) = 24426f6211bd68ce7647ebfd7f694b42` → password = **`ilikegreenkitkat`**.

## Flag
ilikegreenkitkat

## Lessons and reusable patterns
- echo -n (without the final \n) is crucial for a correct hash.
- Tiny search space (6 candidates) -> simple loop, no hashcat needed.
