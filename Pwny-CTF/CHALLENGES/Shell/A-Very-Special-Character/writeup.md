---
title: "A-Very-Special-Character"
ctf: "Pwny-CTF"
category: "misc"
difficulty: "Not specified"
points: 20
techniques: ["encoding"]
tools: ["pwntools", "netcat"]
keywords: ["A-Very-Special-Character", "Pwny-CTF", "misc", "encoding", "pwntools", "netcat", "https", "hex"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Shell/A-Very-Special-Character/notes.md"
---

# A-Very-Special-Character (Pwny-CTF, misc)

## Summary
Challenge **A-Very-Special-Character** from the Pwny-CTF CTF, misc category. Main technique: encoding. ASCII: 0x41=A, 0x61=a, 0x30=0… chr()/ord() in Python, or printf "\x42".

## Statement and artefacts
Here's another challenge that needs you to netcat to a server!

`nc chal.sigpwny.com 5002`

This one is to help familiarize yourself with the ascii table. To see which character has a hex ascii value of 0x42, check out https://www.ascii-code.com/

## Recognition signals
Not specified.

## Resolution method
1. `nc chal.sigpwny.com 5002`: the server requests the character corresponding to an ASCII value in hex (e.g. `0x42` → `B`).
2. Reply with the correct character (ASCII table, e.g. https://www.ascii-code.com/). In Python: `chr(0x42)`.
3. After the correct answers → `sigpwny{ez_pz_ascii!}`.

## Flag
sigpwny{ez_pz_ascii!}

## Lessons and reusable patterns
- ASCII: 0x41=A, 0x61=a, 0x30=0… chr()/ord() in Python, or printf "\x42".
- If there are many rounds -> script with pwntools (chr(int(x,16))).
