---
title: "Pyjail-4"
ctf: "Pwny-CTF"
category: "misc"
difficulty: "Not specified"
points: 250
techniques: ["jail-escape", "pyjail"]
tools: ["netcat", "python"]
keywords: ["Pyjail-4", "Pwny-CTF", "misc", "jail-escape", "pyjail", "netcat", "python"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Python-Jails/Pyjail-4/notes.md"
---

# Pyjail-4 (Pwny-CTF, misc)

## Summary
Challenge **Pyjail-4** from the Pwny-CTF CTF, misc category. Main technique: jail-escape. The flag: sigpwny{stupid_exceptions}

## Statement and artefacts
nc chal.sigpwny.com 5015

Author: Pete

**Provided files / artifacts:**
- `work/Dockerfile (file, 292 B)`
- `work/handout-4.zip (archive, 894 B)`
- `work/info.txt (text, 823 B)`

## Recognition signals
- Signal: The list prohibits most of the usual bricks — but not breakpoint.
- Signal: (Fun bug: 'cat' 'flag' without comma = Python concatenation -> single 'catflag' entry, so neither cat nor flag alone are actually banned.).

## Resolution method
1. Read the blacklist → `import/exec/os/open/chr/input...` blocked, but `breakpoint` absent.
2. Payload (`work/solve.py`): `breakpoint()` → open pdb; the `(Pdb)` prompt is not filtered → `import os; os.system("cat /flag.txt")`.

1. **Flaw (source)**

```python
blacklist = ['import','eval','exec','system','compile','os','chr',
             'input','open','cat' 'flag','txt','"','+']
for bad in blacklist:
    if bad in user_input: return True
...
exec(user_input)          # in a try/except Exception
```
The list bans most common bricks — but not `breakpoint`. (Fun bug: `'cat' 'flag'` without a comma = Python concatenation → single entry `'catflag'`, so neither `cat` nor `flag` alone are actually banned.)

## Solve script
Script path: [scripts/solve.py](scripts/solve.py)

## Flag
sigpwny{stupid_exceptions}

## Lessons and reusable patterns
- Word blacklist = cat and mouse game: all it takes is one forgotten word. breakpoint almost always passes through blacklists that think “import/eval/exec”.
- The title stupid_exceptions points to the try/except Exception: it swallows errors but does not prevent breakpoint() from opening pdb first.
- Spot blacklist bugs: implicit concatenation of strings ('cat' 'flag'), forgetting breakpoint, help, etc.
