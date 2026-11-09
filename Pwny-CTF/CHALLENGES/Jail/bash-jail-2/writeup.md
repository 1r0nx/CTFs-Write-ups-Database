---
title: "bash-jail-2"
ctf: "Pwny-CTF"
category: "misc"
difficulty: "Not specified"
points: 150
techniques: ["jail-escape", "bash-jail"]
tools: ["netcat", "bash", "python"]
keywords: ["bash-jail-2", "Pwny-CTF", "misc", "jail-escape", "bash-jail", "netcat", "bash", "python"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Jail/bash-jail-2/notes.md"
---

# bash-jail-2 (Pwny-CTF, misc)

## Summary
Challenge **bash-jail-2** from the Pwny-CTF CTF, misc category. Main technique: jail-escape. The flag: sigpwny{Big_Brain_Bash_Bois}

## Statement and artefacts
Now, we've banned certain characters as input - can you "bash" your way through this one?

`nc chal.sigpwny.com 5006`

**Author**: Nathan

**Provided files / artifacts:**
- `work/info.txt (text, 553 B)`

## Recognition signals
- Signal: The pattern bans < > ( ) $ * | and the letters A, C–Z, a, c–z.
- Signal: Only b and B remain authorized among the letters (and the numbers, /,?,.).

## Resolution method
1. Read filter → no more `$()`, no more letters except `b`/`B`.
2. Payload (`work/solve.py`): `/b??/b???` → wildcard shell: `/b??` = `/bin`, `/b???` = `/bash` → path `/bin/bash`. `eval` therefore launches an **interactive shell** (here without redirection → we keep control).
3. In this shell, type normally: `cat /flag.txt` → flag.

1. **Flaw (source)**

```bash
if (echo "$input" | grep -E -q ".*[<>()$*|AC-Zac-z]+.*")
then echo "Banned character used!"
else eval "$input"
fi
```
The pattern bans `< > ( ) $ * |` and the letters `A`, `C`–`Z`, `a`, `c`–`z`. **Only `b` and `B` remain authorized** among the letters (and numbers, `/`, `?`,...).

## Solve script
Script path: [scripts/main.sh](scripts/main.sh)
Script path: [scripts/solve.py](scripts/solve.py)

## Flag
sigpwny{Big_Brain_Bash_Bois}

## Lessons and reusable patterns
- Global? = 1 any character: allows you to write the path of a binary without typing the forbidden letters (/b??/b??? -> /bin/bash, //???/c?? -> /bin/cat...).
- Running /bin/bash (or /bin/sh) returns control to a real shell -> the input filter no longer applies.
- Warning: a glob only matches existing files, and can match several paths (choose a fairly specific pattern).
