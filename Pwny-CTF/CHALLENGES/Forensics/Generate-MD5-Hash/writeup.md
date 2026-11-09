---
title: "Generate-MD5-Hash"
ctf: "Pwny-CTF"
category: "forensics"
difficulty: "Not specified"
points: 25
techniques: ["forensics", "hash-cracking"]
tools: []
keywords: ["Generate-MD5-Hash", "Pwny-CTF", "forensics"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Forensics/Generate-MD5-Hash/notes.md"
---

# Generate-MD5-Hash (Pwny-CTF, forensics)

## Summary
Challenge **Generate-MD5-Hash** from the Pwny-CTF CTF, forensics category. Echo -n to not include newline (otherwise different hash).

## Statement and artefacts
Find the MD5 hash of the string sigpwny.

## Recognition signals
Not specified.

## Resolution method
1. `echo -n "sigpwny" | md5sum` → `c69d540bf0c629fb0866fc0128056b01`.

## Flag
c69d540bf0c629fb0866fc0128056b01

## Lessons and reusable patterns
- echo -n to not include the newline (otherwise different hash).
