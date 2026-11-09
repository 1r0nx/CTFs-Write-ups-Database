---
title: "bash-jail-3"
ctf: "Pwny-CTF"
category: "misc"
difficulty: "Not specified"
points: 300
techniques: ["substitution-cipher", "jail-escape", "bash-jail"]
tools: ["netcat", "bash", "python"]
keywords: ["bash-jail-3", "Pwny-CTF", "misc", "substitution-cipher", "jail-escape", "bash-jail", "netcat", "bash", "python"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Jail/bash-jail-3/notes.md"
---

# bash-jail-3 (Pwny-CTF, misc)

## Summary
Challenge **bash-jail-3** from the Pwny-CTF CTF, misc category. Main technique: substitution-cipher. The flag: sigpwny{redirection&misdirection}

## Statement and artefacts
This time, we've banned even more characters - including some special ones. Try to read the flag now!

`nc chal.sigpwny.com 5007`

**Author**: Nathan

**Provided files / artifacts:**
- `work/info.txt (text, 568 B)`

## Recognition signals
- If we look at Banned Letters, think about o r i e n t s.
- If we observe And again > /dev/null, think about blind reading (like bash jail 1).
- Signal: Accumulation of techniques: glob? to bypass the blacklist of letters (bash jail 2) + substitution $(.) to leak by mistake when stdout goes to /dev/null (bash jail 1).

## Resolution method
1. Read filter → `o, r, i, e, n, t, s` forbidden + discarded stdout.
2. Payload (`work/solve.py`): `$(/u??/b??/ca? /flag.???)` → jokers to avoid banned letters: `/u??` = `/usr`, `/b??` = `/bin`, `/ca?` = `/cat` (the `t` of `cat` is banned), `/flag.???` = `/flag.txt`. So `/usr/bin/cat /flag.txt`. → `$(...)` transforms the content of the flag into a command → `command not found: sigpwny{...}` on **stderr**.

1. **Flaw (source)**

```bash
if (echo "$input" | grep -E -q ".*[orients].*")
then echo "Banned character used!"
else eval "$input" > /dev/null
fi
```
Banned letters: `o r i e n t s`. And again `> /dev/null` → blind reading (like bash jail 1).

## Solve script
Script path: [scripts/main.sh](scripts/main.sh)
Script path: [scripts/solve.py](scripts/solve.py)

## Flag
sigpwny{redirection&misdirection}

## Lessons and reusable patterns
- Combination of techniques: glob? to bypass the blacklist of letters (bash jail 2) + substitution $(...) to leak by mistake when stdout goes to /dev/null (bash jail 1).
- Choose the jokers according to the authorized letters: here t, n, s, r, i, o, e are all prohibited, hence ca?, b??, u??,.???.
