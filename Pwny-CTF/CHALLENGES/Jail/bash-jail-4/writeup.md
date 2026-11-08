---
title: "bash-jail-4"
ctf: "Pwny-CTF"
category: "misc"
difficulty: "Not specified"
points: 400
techniques: ["jail-escape", "bash-jail", "encoding"]
tools: ["xxd", "netcat", "python"]
keywords: ["bash-jail-4", "Pwny-CTF", "misc", "jail-escape", "bash-jail", "encoding", "xxd", "netcat", "python", "base64"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Jail/bash-jail-4/notes.md"
---

# bash-jail-4 (Pwny-CTF, misc)

## Summary
Challenge **bash-jail-4** from the Pwny-CTF CTF, misc category. Main technique: jail-escape. The flag: sigpwny{python_and_bash_jail_combo}

## Statement and artefacts
We have a service that will run Bash scripts that you provide it - however, it is quite picky as to which scripts it will run. Can you get it to give you the flag?

`nc chal.sigpwny.com 5008`

**Author**: Husnain

**Provided files / artifacts:**
- `work/Dockerfile (file, 310 B)`
- `work/info.txt (text, 1.0 KB)`

## Recognition signals
- Signal: run.py: we submit a bash script in base64, then executed, but filtered.
- Signal: The filter only looks at the letters [a-zA-Z] present in the script (numbers, /,?, space.
- Signal: Transform the data with a utility (base32, base64, xxd, rev, od) when you need to bypass an output filter or simply a constraint on what you can type, then decode locally.

## Resolution method
1. Read `run.py` → script is only entitled to the letters `n`, `o`, `p`; base64 entry; index = GTFObins + `?` = 1 character.
2. Build the script in globs to not use any forbidden letters: `/???/??n/????32 /????????` = `/usr/bin/base32 /flag.txt` → only literal letter: `n` (in `??n` → `bin`), allowed.
3. Encode it in base64 (`work/solve.py`, `b64e(...)`) and send it. → `base32 /flag.txt` displays the flag **encoded in base32** (so output in A-Z/2-7, it does not “contain” the flag in plain text).
4. Decode offline output: `echo 'ONUW...BI======' | base32 -d` → `sigpwny{python_and_bash_jail_combo}`.

1. **Flaw (source)**

`run.py`: we submit a bash script **in base64**, then executed, but filtered:
```python
allowed_letters = "nop"
return set(letters_used) <= set(allowed_letters)   # only n, o, p allowed
```
The filter only looks at the **letters [a-zA-Z]** present in the script (numbers, `/`, `?`, space, `.` are free).

## Solve script
Script path: `scripts/run.py`
Script path: `scripts/solve.py`

## Flag
sigpwny{python_and_bash_jail_combo}

## Lessons and reusable patterns
- Filter on script letters -> globs? to compose binary paths without typing the letters (/???/??n/...).
- Transform the data with a utility (base32, base64, xxd, rev, od) when you need to bypass an output filter or simply a constraint on what you can type, then decode locally.
- GTFObins reflex: search for an authorized binary capable of reading/displaying a file (here base32 FILE).
