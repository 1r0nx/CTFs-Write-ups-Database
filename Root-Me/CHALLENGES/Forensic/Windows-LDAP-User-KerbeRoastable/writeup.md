---
title: "Windows-LDAP-User-KerbeRoastable"
ctf: "Root-Me"
category: "forensics"
difficulty: "medium"
points: 20
techniques: ["forensics"]
tools: []
keywords: ["Windows-LDAP-User-KerbeRoastable", "Root-Me", "forensics"]
status: "solved"
has_script: false
source: "Root-Me/Forensic/Windows-LDAP-User-KerbeRoastable/solve.txt"
---

# Windows-LDAP-User-KerbeRoastable (Root-Me, forensics)

## Summary
Challenge **Windows-LDAP-User-KerbeRoastable** from the Root-Me CTF, forensics category. Find in the.json servicePrincipalName

## Statement and artefacts

**Official statement (Root-Me, English page):**

During your investigations, you found a backup of the company’s KDAP made with [ldap2json](https://github.com/p0dalirius/ldap2json). Use the information in this dump to find the Kerberoastable user.

The flag is the email address of the Kerberoastable user.

- **Category:** Forensics
- **Difficulty:** Medium
- **Points:** 20
- **Author(s):** Podalirius
- **Published:** 2022-11-17 15:42:53
- **Root-Me page:** https://www.root-me.org/en/Challenges/Forensic/Windows-LDAP-User-KerbeRoastable

**Provided file (as listed on Root-Me):**
- [`ch31.json`](https://static.root-me.org/forensic/ch31/ch31.json) — challenge dump.

## Recognition signals
Not specified.

## Resolution method
1. find in the.json servicePrincipalName

## Flag
alexandria.newton@rootme.local

## Lessons and reusable patterns
Not specified.
