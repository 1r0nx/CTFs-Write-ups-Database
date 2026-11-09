---
title: "the-library-3"
ctf: "Pwny-CTF"
category: "misc"
difficulty: "Not specified"
points: 50
techniques: ["misc"]
tools: []
keywords: ["the-library-3", "Pwny-CTF", "misc", "zip"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Shell/the-library-3/notes.md"
---

# the-library-3 (Pwny-CTF, misc)

## Summary
Challenge **the-library-3** from the Pwny-CTF CTF, misc category. Grep -r recursively searches content; -a (binary->text), -o (as the match).

## Statement and artefacts
There is a file in the zip that has a flag *inside* it. Can you find it somehow?!?

## Recognition signals
Not specified.

## Resolution method
1. Statement: *“a file in the zip has a flag *inside* it”* → the flag is in the **contents** of a file.
2. `grep -rao "sigpwny{[^}]*}" findme/` → `findme/6/3/8/2/ubjLqN.txt: sigpwny{get_a_grep_on_the_situation}`.
3. Flag = `sigpwny{get_a_grep_on_the_situation}` (checked: same as flag.txt).

## Flag
sigpwny{get_a_grep_on_the_situation}

## Lessons and reusable patterns
- grep -r recursively searches the content; -a (binary->text), -o (as the match).
- Archive shared with the entire the-library series (the-library-2/SIGPwny-Chals-FA2020/findme).
