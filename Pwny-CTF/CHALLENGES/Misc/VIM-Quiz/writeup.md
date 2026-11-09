---
title: "VIM-Quiz"
ctf: "Pwny-CTF"
category: "misc"
difficulty: "Not specified"
points: 100
techniques: ["aes", "crypto"]
tools: ["pwntools", "netcat", "python"]
keywords: ["VIM-Quiz", "Pwny-CTF", "misc", "pwntools", "netcat", "python"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Misc/VIM-Quiz/notes.md"
---

# VIM-Quiz (Pwny-CTF, misc)

## Summary
Challenge **VIM-Quiz** from the Pwny-CTF CTF, misc category. Enter insert mode -> i 2.

## Statement and artefacts
Do you know VIM?

nc chal.sigpwny.com 5094

author: richard

**Provided files / artifacts:**

## Recognition signals
Not specified.

## Resolution method
1. **The idea**

Interactive quiz (`nc chal.sigpwny.com 5094`): 4 questions on VIM shortcuts. Response format: a key combination = modifier + `-` (e.g. Ctrl+[ → `c-[`).

## Solve script
Script path: [scripts/solve.py](scripts/solve.py)

## Flag
sigpwny{v1m_h4s_a_5hall0w_l3arn1ng_curv3}

## Lessons and reusable patterns
- Enter insert mode -> i 2.
- GB to end of line (normal mode) -> $3.
- Repeat last command ->.
- Equivalent to Esc key -> c-[ (Ctrl+[)
- -> sigpwny{v1m_h4s_a_5hall0w_l3arn1ng_curv3}
- Quiz on server: script the question reading -> answer via pwntools
- Basic VIM shortcuts: i (insert), $/0 (end/start of line),. (repeat),
