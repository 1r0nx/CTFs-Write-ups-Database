---
title: "Shell-Basics-3-Terminate"
ctf: "Pwny-CTF"
category: "misc"
difficulty: "Not specified"
points: 20
techniques: ["aes"]
tools: []
keywords: ["Shell-Basics-3-Terminate", "Pwny-CTF", "misc"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Shell/Shell-Basics-3-Terminate/notes.md"
---

# Shell-Basics-3-Terminate (Pwny-CTF, misc)

## Summary
Challenge **Shell-Basics-3-Terminate** from the Pwny-CTF CTF, misc category. Ctrl-C sends SIGINT (stop); Ctrl-Z suspend (SIGTSTP).

## Statement and artefacts
Navigate to `/3-learn-how-to-stop-programs-with-ctrl-c` and search for the flag

`ssh shell@chal.sigpwny.com -p 8022`

Password is `pineapple`

Flag format: `flag{...}`

## Recognition signals
Not specified.

## Resolution method
1. SSH then `cd /3-learn-how-to-stop-programs-with-ctrl-c`.
2. Start the program, interrupt it with **Ctrl-C** (SIGINT) → the flag is displayed.
3. `flag{sometimes_you_just_gotta_stop}`.

## Flag
flag{sometimes_you_just_gotta_stop}

## Lessons and reusable patterns
- Ctrl-C sends SIGINT (stop); Ctrl-Z suspend (SIGTSTP).
