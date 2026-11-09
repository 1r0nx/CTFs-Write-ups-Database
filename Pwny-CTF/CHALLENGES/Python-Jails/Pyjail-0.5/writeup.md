---
title: "Pyjail-0.5"
ctf: "Pwny-CTF"
category: "misc"
difficulty: "Not specified"
points: 30
techniques: ["jail-escape", "pyjail"]
tools: ["netcat", "python"]
keywords: ["Pyjail-0.5", "Pwny-CTF", "misc", "jail-escape", "pyjail", "netcat", "python"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Python-Jails/Pyjail-0.5/notes.md"
---

# Pyjail-0.5 (Pwny-CTF, misc)

## Summary
Challenge **Pyjail-0.5** from the Pwny-CTF CTF, misc category. Main technique: jail-escape. The flag: sigpwny{but_but_i_used_eval_what_nooooo}

## Statement and artefacts
nc chal.sigpwny.com 5010

Author: Pete

**Provided files / artifacts:**
- `work/Dockerfile (file, 292 B)`
- `work/handout-0.5.zip (archive, 886 B)`
- `work/info.txt (text, 764 B)`

## Recognition signals
- Signal: Two constraints: eval only accepts one expression (no import os), and we cannot write flag.

## Resolution method
1. Read filter → `eval` + `'flag'` banned.
2. Payload (`work/solve.py`): `__import__('os').system('cat /????.txt')` → `__import__('os')` works around the absence of `import` in a `eval`; `/????.txt` (wildcard shell) avoids the word `flag`.

1. **Flaw (source)**

```python
def is_bad(user_input):
    return 'flag' in user_input     # the word "flag" is prohibited
...
eval(user_input)                    # eval, not exec
```
Two constraints: `eval` only accepts one **expression** (no `import os`), and we cannot write `flag`.

## Solve script
Script path: [scripts/solve.py](scripts/solve.py)

## Flag
sigpwny{but_but_i_used_eval_what_nooooo}

## Lessons and reusable patterns
- open eval -> __import__('os').system(...) (a single expression, no statement).
- Filtered keyword in file name -> replace with a glob: /????.txt, /fl*, /f?ag.txt. The shell resolves the pattern.
- Same family as Calculator Escape 0/1.
