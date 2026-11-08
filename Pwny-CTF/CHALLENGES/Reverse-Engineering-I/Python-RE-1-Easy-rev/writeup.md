---
title: "Python-RE-1-Easy-rev"
ctf: "Pwny-CTF"
category: "reverse"
difficulty: "easy"
points: 75
techniques: ["xor-cipher", "reverse-engineering", "vm-reverse"]
tools: []
keywords: ["Python-RE-1-Easy-rev", "Pwny-CTF", "reverse", "xor-cipher", "reverse-engineering", "vm-reverse", "xor"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Reverse-Engineering-I/Python-RE-1-Easy-rev/notes.md"
---

# Python-RE-1-Easy-rev (Pwny-CTF, reverse)

## Summary
Challenge **Python-RE-1-Easy-rev** from the Pwny-CTF CTF, reverse category. Main technique: xor-cipher. Don't get distracted by the interaction (the quiz): follow the data flow that produces the flag.

## Statement and artefacts
I made a little quiz. It has a little flag.

Author: Juniper

## Recognition signals
Not specified.

## Resolution method
1. Read `chal.py`: the flag is reconstructed by `XOR` (key `encrypt1`) + **permutation** (`encrypt2`) from a large integer, then `XOR n`.
2. The condition `if n == 0x4d9a...` is **always true** → the calculation of the flag does not depend on the answers to the quiz.
3. Re-execute only the calculation part (or run the script and answer anything to the quiz, the `if` still passes) → `sigpwny{5cr4mbl3d_xors}` (checked).

## Flag
sigpwny{5cr4mbl3d_xors}

## Lessons and reusable patterns
- Don't get distracted by the interaction (the quiz): follow the data flow that produces the flag.
- Classic techniques: repeated key XOR + scramble (permutation of indices) -> reversible by rereading the code.
- The simplest: copy/paste the calculation logic into a Python interpreter.
- (See the course Reverse-Engineering-I.pdf.)
