---
title: "Pyjail-1"
ctf: "Pwny-CTF"
category: "misc"
difficulty: "Not specified"
points: 150
techniques: ["jail-escape", "pyjail"]
tools: ["netcat", "python"]
keywords: ["Pyjail-1", "Pwny-CTF", "misc", "jail-escape", "pyjail", "netcat", "python"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Python-Jails/Pyjail-1/notes.md"
---

# Pyjail-1 (Pwny-CTF, misc)

## Summary
Challenge **Pyjail-1** from the Pwny-CTF CTF, misc category. Main technique: jail-escape. The flag: sigpwny{just_warming_up}

## Statement and artefacts
nc chal.sigpwny.com 5012

Author: Pete

**Provided files / artifacts:**
- `work/Dockerfile (file, 292 B)`
- `work/handout-1.zip (archive, 840 B)`
- `work/info.txt (text, 713 B)`

## Recognition signals
- Signal: Naive filter: it forgets single quotes '.
- When a filter bans ", think of single quotes ' (and vice versa), or triples, or chr().

## Resolution method
1. Read filter → prohibited: `"` and `*` only.
2. Payload (`work/solve.py`): `import os; os.system('cat /flag.txt')` → replace double quotes with single ones; no `*` needed.

1. **Flaw (source)**

```python
banned = '"*'        # only " and * are prohibited
...
exec(user_input)
```
Naive filter: it forgets the **single** quotes `'`.

## Solve script
Script path: `scripts/solve.py`

## Flag
sigpwny{just_warming_up}

## Lessons and reusable patterns
- When a filter bans ", think of single quotes ' (and vice versa), or triples, or chr().
- open exec + just 2 forbidden characters = trivial escape; always list exactly what is banned before complicating.
