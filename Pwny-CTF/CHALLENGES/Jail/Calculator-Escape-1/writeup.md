---
title: "Calculator-Escape-1"
ctf: "Pwny-CTF"
category: "misc"
difficulty: "Not specified"
points: 50
techniques: ["jail-escape", "pyjail"]
tools: ["netcat"]
keywords: ["Calculator-Escape-1", "Pwny-CTF", "misc", "jail-escape", "pyjail", "netcat"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Jail/Calculator-Escape-1/notes.md"
---

# Calculator-Escape-1 (Pwny-CTF, misc)

## Summary
Challenge **Calculator-Escape-1** from the Pwny-CTF CTF, misc category. Main technique: jail-escape. The flag: sigpwny{dont_quote_me_on_that}

## Statement and artefacts
Can you pwn this calculator challenge and read /flag.txt?

`nc chal.sigpwny.com 7002`

**author**: Nathan

**Provided files / artifacts:**
- `work/info.txt (text, 577 B)`

## Recognition signals
- Signal: Without quotes you cannot write a literal string; without i/b you cannot type __import__ or bytes directly.
- Signal: Glob shell /????.txt = wildcard for /flag.txt when the word flag or certain letters are filtered.

## Resolution method
1. Read the filter → prohibited: `"` `'` `` ` `` and the letters `i`, `b`.
2. Construct each character with `chr(n)` (the `+` concatenates), then `exec(...)` the resulting string:
   ```python
   exec(chr(95)+chr(95)+chr(105)+...+chr(41))
   # = exec("__import__('os').system('cat /????.txt')")
   ```
`exec` and `chr` do not contain any banned characters; `chr(105)` provides the forbidden `i` to the keyboard. The file name uses `????` (glob shell) to avoid retyping `flag`.

1. **Flaw (source)**

```python
not_allowed = set('"\'`ib')     # quotation marks ", ', ` and the letters i, b banned
return any(c in not_allowed for c in s)
...
eval(s)
```
Without quotes you cannot write a literal string; without `i`/`b` you cannot type `__import__` nor `bytes` directly.

## Flag
sigpwny{dont_quote_me_on_that}

## Lessons and reusable patterns
- Filter on characters -> chr()/ord() to reconstruct forbidden letters/quotes, + to assemble.
- eval can call exec(...) (it's a function) -> we end up with arbitrary code.
- Glob shell /????.txt = wildcard for /flag.txt when the word flag or certain letters are filtered.
