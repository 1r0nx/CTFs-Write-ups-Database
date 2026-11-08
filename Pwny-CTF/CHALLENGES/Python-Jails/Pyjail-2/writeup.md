---
title: "Pyjail-2"
ctf: "Pwny-CTF"
category: "misc"
difficulty: "Not specified"
points: 200
techniques: ["jail-escape", "pyjail"]
tools: ["netcat", "python"]
keywords: ["Pyjail-2", "Pwny-CTF", "misc", "jail-escape", "pyjail", "netcat", "python"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Python-Jails/Pyjail-2/notes.md"
---

# Pyjail-2 (Pwny-CTF, misc)

## Summary
Challenge **Pyjail-2** from the Pwny-CTF CTF, misc category. Main technique: jail-escape. The flag: sigpwny{dont_quote_me_on_that}

## Statement and artefacts
nc chal.sigpwny.com 5013

Author: Pete

**Provided files / artifacts:**
- `work/Dockerfile (file, 292 B)`
- `work/handout-2.zip (archive, 840 B)`
- `work/info.txt (text, 810 B)`

## Recognition signals
- Signal: No more quotation marks possible -> we cannot write a literal string; x prohibits case also exec(.) written by hand.

## Resolution method
1. Read filter → `"` `'` `` ` `` `*` `x` banned.
2. Payload (`work/solve.py`): `breakpoint()` (no banned characters). → opens `pdb`; in the `(Pdb)` prompt, the filter no longer applies → `import os; os.system("cat /flag.txt")`.

1. **Flaw (source)**

```python
banned = '"*\'`x'    #", ', `, *, and the letter x
...
exec(user_input)
```
No more quotation marks possible → we cannot write a literal string; `x` forbidden case also `exec(...)` written by hand.

## Solve script
Script path: `scripts/solve.py`

## Flag
sigpwny{dont_quote_me_on_that}

## Lessons and reusable patterns
- breakpoint() = boilerplate: contains neither quotes nor “exotic” characters, and the pdb shell it opens is not filtered.
- As soon as a filter blocks all quotes, stop trying to write a string: switch to breakpoint() (or help(), another escape via a sub-prompt).
- Same technique as Calculator Escape 2; flag identical to another challenge, don't be surprised.
