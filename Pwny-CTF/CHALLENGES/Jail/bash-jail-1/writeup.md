---
title: "bash-jail-1"
ctf: "Pwny-CTF"
category: "misc"
difficulty: "Not specified"
points: 100
techniques: ["substitution-cipher", "command-injection", "jail-escape", "bash-jail"]
tools: ["netcat", "bash", "python"]
keywords: ["bash-jail-1", "Pwny-CTF", "misc", "substitution-cipher", "command-injection", "jail-escape", "bash-jail", "netcat", "bash", "python"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Jail/bash-jail-1/notes.md"
---

# bash-jail-1 (Pwny-CTF, misc)

## Summary
Challenge **bash-jail-1** from the Pwny-CTF CTF, misc category. Main technique: substitution-cipher. The flag: sigpwny{$h3l1_sP4wner}

## Statement and artefacts
This time, I've made it so that you can't see the output of your commands. Can you still read the flag?

`nc chal.sigpwny.com 5005`

**Author**: Nathan

**Provided files / artifacts:**
- `work/info.txt (text, 542 B)`

## Recognition signals
- Signal: We cannot see the stdout of our commands, but stderr remains visible.

## Resolution method
1. Read `main.sh` → `eval "$input" >/dev/null`: “blind” reading.
2. Payload (`work/solve.py`): `$(cat /flag.txt)` → `$(...)` reads the flag and substitutes it as **command to execute**. `sigpwny{...}` is not a valid command → bash shouts **stderr**: `./main.sh: line 9: sigpwny{$h3l1_sP4wner}: command not found` → the flag is in the message.

1. **Flaw (source)**

```bash
read input
eval "$input" > /dev/null    # stdout thrown, but not stderr
```
We cannot see the stdout of our commands, but stderr remains visible.

## Solve script
Script path: `scripts/main.sh`
Script path: `scripts/solve.py`

## Flag
sigpwny{$h3l1_sP4wner}

## Lessons and reusable patterns
- stdout to /dev/null ≠ stderr: errors often remain displayed. Transforming the secret data into an invalid command ($(cat flag)) forces a command not found: <flag>.
- “Blind command exec” reflex: exfiltrate by mistake, or redirect the output yourself (file, network).
