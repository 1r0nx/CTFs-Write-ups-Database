---
title: "Shell-Basics-4-Hidden-Files"
ctf: "Pwny-CTF"
category: "misc"
difficulty: "Not specified"
points: 20
techniques: []
tools: []
keywords: ["Shell-Basics-4-Hidden-Files", "Pwny-CTF", "misc"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Shell/Shell-Basics-4-Hidden-Files/notes.md"
---

# Shell-Basics-4-Hidden-Files (Pwny-CTF, misc)

## Summary
Challenge **Shell-Basics-4-Hidden-Files** from the Pwny-CTF CTF, misc category. On Unix, a file whose name begins with. is hidden; ls -a reveals them.

## Statement and artefacts
Navigate to `/4-learn-about-hidden-files` and search for the flag

`ssh shell@chal.sigpwny.com -p 8022`

Password is `pineapple`

Flag format: `flag{...}`

## Recognition signals
Not specified.

## Resolution method
1. SSH then `cd /4-learn-about-hidden-files`.
2. `ls -a` (or `ls -la`) to see hidden files, then `cat .<file>`.
3. `flag{sometimes_you_just_gotta_look_harder}`.

## Flag
flag{sometimes_you_just_gotta_look_harder}

## Lessons and reusable patterns
- On Unix, a file whose name begins with. is hidden; ls -a reveals them.
