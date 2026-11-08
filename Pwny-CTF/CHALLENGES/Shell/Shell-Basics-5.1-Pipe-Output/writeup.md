---
title: "Shell-Basics-5.1-Pipe-Output"
ctf: "Pwny-CTF"
category: "misc"
difficulty: "Not specified"
points: 20
techniques: []
tools: []
keywords: ["Shell-Basics-5.1-Pipe-Output", "Pwny-CTF", "misc"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Shell/Shell-Basics-5.1-Pipe-Output/notes.md"
---

# Shell-Basics-5.1-Pipe-Output (Pwny-CTF, misc)

## Summary
Challenge **Shell-Basics-5.1-Pipe-Output** from the Pwny-CTF CTF, misc category. Cmd1 | cmd2: chain commands (grep, sort, wc…).

## Statement and artefacts
`ssh shell@chal.sigpwny.com -p 8022`

password is `pineapple`

Flag format: `sigpwny{...}`

## Recognition signals
Not specified.

## Resolution method
1. SSH; follow the instructions in the file: send the output of one command to another via `|` (e.g. `cat file | <prog>`).
2. `sigpwny{whats_a_pipe}`.

## Flag
sigpwny{whats_a_pipe}

## Lessons and reusable patterns
- cmd1 | cmd2: chain commands (grep, sort, wc…).
