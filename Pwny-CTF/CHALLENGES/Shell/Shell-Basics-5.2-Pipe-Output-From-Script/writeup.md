---
title: "Shell-Basics-5.2-Pipe-Output-From-Script"
ctf: "Pwny-CTF"
category: "misc"
difficulty: "Not specified"
points: 20
techniques: []
tools: []
keywords: ["Shell-Basics-5.2-Pipe-Output-From-Script", "Pwny-CTF", "misc"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Shell/Shell-Basics-5.2-Pipe-Output-From-Script/notes.md"
---

# Shell-Basics-5.2-Pipe-Output-From-Script (Pwny-CTF, misc)

## Summary
Challenge **Shell-Basics-5.2-Pipe-Output-From-Script** from the Pwny-CTF CTF, misc category. Automate: generate the data using a script then | — more reliable than typing by hand.

## Statement and artefacts
`ssh shell@chal.sigpwny.com -p 8022`

password is `pineapple`

Flag format: `sigpwny{...}`

## Recognition signals
Not specified.

## Resolution method
1. SSH; run the script and pipe its output to the target program (`./script.sh | <prog>` or `python3 x.py | <prog>`).
2. `sigpwny{i_hope_you_didnt_type_that_by_hand}`.

## Flag
sigpwny{i_hope_you_didnt_type_that_by_hand}

## Lessons and reusable patterns
- Automate: generate the data using a script then | — more reliable than typing by hand.
