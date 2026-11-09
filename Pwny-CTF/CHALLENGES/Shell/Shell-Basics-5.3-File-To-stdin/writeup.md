---
title: "Shell-Basics-5.3-File-To-stdin"
ctf: "Pwny-CTF"
category: "misc"
difficulty: "Not specified"
points: 20
techniques: ["misc"]
tools: []
keywords: ["Shell-Basics-5.3-File-To-stdin", "Pwny-CTF", "misc"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Shell/Shell-Basics-5.3-File-To-stdin/notes.md"
---

# Shell-Basics-5.3-File-To-stdin (Pwny-CTF, misc)

## Summary
Challenge **Shell-Basics-5.3-File-To-stdin** from the Pwny-CTF CTF, misc category. Cmd < file = send the contents of the file to the cmd input (≠ | which comes from another command).

## Statement and artefacts
`ssh shell@chal.sigpwny.com -p 8022`

password is `pineapple`

Flag format: `sigpwny{...}`

## Recognition signals
Not specified.

## Resolution method
1. SSH; provide a file as standard input: `<prog> <file`.
2. `sigpwny{i_hope_you_didnt_cheat_by_using_pipe}`.

## Flag
sigpwny{i_hope_you_didnt_cheat_by_using_pipe}

## Lessons and reusable patterns
- cmd < file = send the contents of the file to the cmd input (≠ | which comes from another command).
