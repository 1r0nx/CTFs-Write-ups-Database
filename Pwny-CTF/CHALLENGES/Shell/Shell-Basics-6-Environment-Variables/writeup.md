---
title: "Shell-Basics-6-Environment-Variables"
ctf: "Pwny-CTF"
category: "misc"
difficulty: "Not specified"
points: 20
techniques: ["misc"]
tools: []
keywords: ["Shell-Basics-6-Environment-Variables", "Pwny-CTF", "misc"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Shell/Shell-Basics-6-Environment-Variables/notes.md"
---

# Shell-Basics-6-Environment-Variables (Pwny-CTF, misc)

## Summary
Challenge **Shell-Basics-6-Environment-Variables** from the Pwny-CTF CTF, misc category. Env/printenv list variables; echo $NAME reads; export NAME=val defines.

## Statement and artefacts
`ssh shell@chal.sigpwny.com -p 8022`

password is `pineapple`

Flag format: `sigpwny{...}`

## Recognition signals
Not specified.

## Resolution method
1. SSH; list the environment: `env` (or `printenv`) → locate the variable containing the flag; `echo $VAR`.
2. `sigpwny{1337_environment}`.

## Flag
sigpwny{1337_environment}

## Lessons and reusable patterns
- env/printenv list variables; echo $NAME reads; export NAME=val defines.
