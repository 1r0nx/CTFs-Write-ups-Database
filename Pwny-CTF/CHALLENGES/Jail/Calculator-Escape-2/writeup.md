---
title: "Calculator-Escape-2"
ctf: "Pwny-CTF"
category: "misc"
difficulty: "Not specified"
points: 125
techniques: ["jail-escape", "pyjail"]
tools: ["netcat"]
keywords: ["Calculator-Escape-2", "Pwny-CTF", "misc", "jail-escape", "pyjail", "netcat"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Jail/Calculator-Escape-2/notes.md"
---

# Calculator-Escape-2 (Pwny-CTF, misc)

## Summary
Challenge **Calculator-Escape-2** from the Pwny-CTF CTF, misc category. Main technique: jail-escape. The flag: sigpwny{exec_anything}

## Statement and artefacts
Can you pwn this calculator challenge and read /flag.txt?

`nc chal.sigpwny.com 7003`

**author**: Nathan

**Provided files / artifacts:**
- `work/info.txt (text, 332 B)`

## Recognition signals
- Signal: The payload must be 15 characters long — too short for an __import__(.).
- Signal: But the limit only applies to this entry.

## Resolution method
1. Read filter → entry limited to 15 characters.
2. Input: `breakpoint()` (12 characters, maximum). → `breakpoint()` launches **pdb**, the interactive Python debugger.
3. In the `(Pdb)` prompt, no more limits: `import os; os.system("cat /flag.txt")` → flag.

1. **Flaw (source)**

```python
def is_input_bad(s):
    return len(s) > 15     # only the 1st line is limited to 15 characters
...
eval(s)
```
The payload must be 15 characters long — too short for `__import__(...)`. But the limit only applies to **this** entry.

## Flag
sigpwny{exec_anything}

## Lessons and reusable patterns
- breakpoint() (Python 3.7+) opens pdb from eval/exec: the prompt (Pdb) executes free Python, without length or character filter. Ultra-short, generic pajail escape.
- Always look at what the filter covers: here the limit only covers the first entry, not the pdb shell opened afterwards.
- Variant: __import__('pdb').set_trace() does the same but is longer.
