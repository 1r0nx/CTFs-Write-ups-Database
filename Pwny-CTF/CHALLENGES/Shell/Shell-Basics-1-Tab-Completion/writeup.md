---
title: "Shell-Basics-1-Tab-Completion"
ctf: "Pwny-CTF"
category: "misc"
difficulty: "Not specified"
points: 20
techniques: ["crypto"]
tools: []
keywords: ["Shell-Basics-1-Tab-Completion", "Pwny-CTF", "misc"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Shell/Shell-Basics-1-Tab-Completion/notes.md"
---

# Shell-Basics-1-Tab-Completion (Pwny-CTF, misc)

## Summary
Challenge **Shell-Basics-1-Tab-Completion** from the Pwny-CTF CTF, misc category. Tab complete file/command names; double-Tab lists the possibilities.

## Statement and artefacts
Navigate to `1-learn-about-tab-completion/` and search for the flag there

`ssh shell@chal.sigpwny.com -p 8022`

password is `pineapple`

Flag format: `flag{...}`

## Recognition signals
Not specified.

## Resolution method
1. `ssh shell@chal.sigpwny.com -p 8022` (pwm `pineapple`).
2. `cd 1-learn-about-tab-completion/` (**Tab** key to complete), then `ls` + `cat` the flag file.
3. `flag{without-tab-completion-my-fingers-may-fall-off}`.

## Flag
flag{without-tab-completion-my-fingers-may-fall-off}

## Lessons and reusable patterns
- Tab complete filenames/commands; double-Tab lists the possibilities.
