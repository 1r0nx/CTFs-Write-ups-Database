---
title: "Pyjail-5"
ctf: "Pwny-CTF"
category: "misc"
difficulty: "Not specified"
points: 300
techniques: ["jail-escape", "pyjail"]
tools: ["netcat", "python"]
keywords: ["Pyjail-5", "Pwny-CTF", "misc", "jail-escape", "pyjail", "netcat", "python"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Python-Jails/Pyjail-5/notes.md"
---

# Pyjail-5 (Pwny-CTF, misc)

## Summary
Challenge **Pyjail-5** from the Pwny-CTF CTF, misc category. Main technique: jail-escape. The flag: sigpwny{who_needs_special_chars_anyways}

## Statement and artefacts
nc chal.sigpwny.com 5016

Author: Pete

**Provided files / artifacts:**
- `work/Dockerfile (file, 292 B)`
- `work/handout-5.zip (archive, 966 B)`
- `work/info.txt (text, 836 B)`

## Recognition signals
- Signal: Comparison in lowercase -> you can't fool with case.
- Signal: Many special characters banned (_.
- If we observe ", think of * $.), but neither breakpoint nor ( ).

## Resolution method
1. Read the blacklist → words and symbols prohibited, but `breakpoint`, `(`, `)` absent.
2. Payload (`work/solve.py`): `breakpoint()` → pdb; in `(Pdb)`, no filter → `import os; os.system("cat /flag.txt")`.

1. **Flaw (source)**

```python
blacklist = ['import','eval','exec','system','compile','os','chr',
             'input','open','cat','lower', 'L','+','ratio','flag','.',
             'txt','!','@','#','$','%','^','&','*','[',']','_','"',':']
for bad in blacklist:
    if bad.lower() in user_input.lower(): return True   # case insensitive
...
exec(user_input)
```
Comparison in lowercase → you can't fool with case. Many special characters banned (`_. ": * $...`), but **neither `breakpoint`, nor `(` `)`**.

## Solve script
Script path: `scripts/solve.py`

## Flag
sigpwny{who_needs_special_chars_anyways}

## Lessons and reusable patterns
- Same lesson as Pyjail 2/4: breakpoint() ignores the blacklist because the dangerous code is typed after, in pdb.
- “Case insensitive” blacklist (.lower()) closes the OS/Os trick, but is of no use if the escape keyword is not listed.
- The flag (who_needs_special_chars_anyways) confirms: no need for banned characters, just open a subshell.
