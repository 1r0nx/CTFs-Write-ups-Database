---
title: "basic64"
ctf: "Pwny-CTF"
category: "reverse"
difficulty: "Not specified"
points: 100
techniques: ["reverse-engineering", "encoding"]
tools: ["python"]
keywords: ["basic64", "Pwny-CTF", "reverse", "reverse-engineering", "encoding", "python", "base64"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Reverse-Engineering-I/basic64/notes.md"
---

# basic64 (Pwny-CTF, reverse)

## Summary
Challenge **basic64** from the Pwny-CTF CTF, reverse category. Main technique: reverse-engineering. Base64 = encoding, not encryption: reversible, and not even necessary here — the flag is in plain text.

## Statement and artefacts
A python RE chal? You don't see that too often. This script has been obfuscated by a state-of-the-art obfuscator. Usage: `python3 basic64.py`

## Recognition signals
Not specified.

## Resolution method
1. The script stacks `exec(b64decode(...))` layers to appear obfuscated.
2. But the flag is **written in plain text** in the final comparison: `grep -ao "sigpwny{[^}]*}" basic64.py`.
3. Flag = `sigpwny{base64_is_not_encryption}` (checked).

## Solve script
Script path: `scripts/basic64.py`

## Flag
sigpwny{base64_is_not_encryption}

## Lessons and reusable patterns
- base64 = encoding, not encryption: reversible, and not even necessary here — the flag is in plain text.
- RE Python reflex: first read/grep the source before unrolling the obfuscation. To unroll cleanly: peel the b64decode layers, or replace exec with print.
- (See the course Reverse-Engineering-I.pdf.)
