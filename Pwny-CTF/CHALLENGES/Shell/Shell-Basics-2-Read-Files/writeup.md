---
title: "Shell-Basics-2-Read-Files"
ctf: "Pwny-CTF"
category: "misc"
difficulty: "Not specified"
points: 20
techniques: []
tools: []
keywords: ["Shell-Basics-2-Read-Files", "Pwny-CTF", "misc"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Shell/Shell-Basics-2-Read-Files/notes.md"
---

# Shell-Basics-2-Read-Files (Pwny-CTF, misc)

## Summary
Challenge **Shell-Basics-2-Read-Files** from the Pwny-CTF CTF, misc category. Cat displays content; less/head/tail for large files.

## Statement and artefacts
Navigate to `/2-learn-to-print-files-on-the-command-line` and search for the flag

`ssh shell@chal.sigpwny.com -p 8022`

Password is `pineapple`

Flag format: `flag{...}`

## Recognition signals
Not specified.

## Resolution method
1. SSH then `cd /2-learn-to-print-files-on-the-command-line`.
2. `ls` then `cat <file>` → `flag{wow_who_new_that_a_cat_could_reveal_everything_within}`.

## Flag
flag{wow_who_new_that_a_cat_could_reveal_everything_within}

## Lessons and reusable patterns
- cat displays the content; less/head/tail for large files.
