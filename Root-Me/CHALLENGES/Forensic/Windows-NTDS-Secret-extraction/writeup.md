---
title: "Windows-NTDS-Secret-extraction"
ctf: "Root-Me"
category: "forensics"
difficulty: "Not specified"
points: null
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
**Provided files / artifacts:**
- `ch34.zip (archive, 9.6 MB)`

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
