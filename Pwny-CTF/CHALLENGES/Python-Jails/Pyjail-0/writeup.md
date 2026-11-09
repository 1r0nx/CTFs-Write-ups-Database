---
title: "Pyjail-0"
ctf: "Pwny-CTF"
category: "misc"
difficulty: "Not specified"
points: 20
techniques: ["jail-escape", "pyjail"]
tools: ["pwntools", "netcat", "python"]
keywords: ["Pyjail-0", "Pwny-CTF", "misc", "jail-escape", "pyjail", "pwntools", "netcat", "python"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Python-Jails/Pyjail-0/notes.md"
---

# Pyjail-0 (Pwny-CTF, misc)

## Summary
Challenge **Pyjail-0** from the Pwny-CTF CTF, misc category. Main technique: jail-escape. The flag: sigpwny{i_always_trust_the_user}

## Statement and artefacts
nc chal.sigpwny.com 5009

Author: Pete

**Provided files / artifacts:**
- `work/Dockerfile (file, 292 B)`
- `work/handout.zip (archive, 834 B)`
- `work/info.txt (text, 729 B)`

## Recognition signals
- If we observe exec (unlike eval) accepts statements, think about import os.
- Signal: works directly.

## Resolution method
1. Read `chal.py` → `is_bad` returns `False`, raw `exec`.
2. Payload (`work/solve.py`): `import os; os.system("cat /flag.txt")` → import authorized because we are in `exec`; `os.system` reads the flag.

1. **Flaw (source)**

```python
def is_bad(user_input):
    return False      # non-existent sandbox
...
exec(user_input)
```
`exec` (unlike `eval`) accepts **statements** → `import os;...` works directly.

## Solve script
Script path: [scripts/solve.py](scripts/solve.py)

## Flag
sigpwny{i_always_trust_the_user}

## Lessons and reusable patterns
- exec vs eval: exec executes statements (import,;, assignments), eval only an expression. With exec open, import os; os.system('cat /flag.txt') is enough.
- Script pwntools type: remote() + sendlineafter(b"yourself?", payload) + interactive().
