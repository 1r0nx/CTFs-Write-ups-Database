---
title: "Windows-NTDS-Secret-extraction"
ctf: "Root-Me"
category: "forensics"
difficulty: "medium"
points: 20
techniques: ["forensics"]
tools: ["impacket"]
keywords: ["Windows-NTDS-Secret-extraction", "Root-Me", "forensics", "impacket"]
status: "solved"
has_script: false
source: "Root-Me/Forensic/Windows-NTDS-Secret-extraction/solve.txt"
---

# Windows-NTDS-Secret-extraction (Root-Me, forensics)

## Summary
Challenge **Windows-NTDS-Secret-extraction** from the Root-Me CTF, forensics category. The Windows-NTDS-Secret-extraction (Root-Me, forensics) challenge is documented by a resolution note.

## Statement and artefacts

**Official statement (Root-Me, English page):**

You have a backup of the registry and NTDS of a Windows server hosting an Active Directory. Can you extract its secrets from these files?

The flag is the key **aes256-cts-hmac-sha1-96** of the **krbtgt** account.

- **Category:** Forensics
- **Difficulty:** Medium
- **Points:** 20
- **Author(s):** Podalirius
- **Published:** 2022-11-17 15:42:50
- **Root-Me page:** https://www.root-me.org/en/Challenges/Forensic/Windows-NTDS-Secret-extraction

**Provided file (as listed on Root-Me):**
- [`ch34.zip`](https://static.root-me.org/forensic/ch34/ch34.zip) — challenge archive.

## Recognition signals
Not specified.

## Resolution method
```
secretsdump.py -system regbackup/registry/SYSTEM -sam regbackup/registry/SAM -security regbackup/registry/SECURITY -ntds regbackup/"Active Directory"/ntds.dit LOCAL | grep -i "krbtgt"
```

## Flag
85c422e6d4f4e340b445c6a3f16d8d7b25bfdf290d956134bc0d5b6ab272b475

## Lessons and reusable patterns
Not specified.
