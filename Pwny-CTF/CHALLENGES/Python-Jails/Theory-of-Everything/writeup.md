---
title: "Theory-of-Everything"
ctf: "Pwny-CTF"
category: "misc"
difficulty: "Not specified"
points: 400
techniques: ["jail-escape", "encoding"]
tools: ["netcat", "python"]
keywords: ["Theory-of-Everything", "Pwny-CTF", "misc", "jail-escape", "encoding", "netcat", "python", "base64"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Python-Jails/Theory-of-Everything/notes.md"
---

# Theory-of-Everything (Pwny-CTF, misc)

## Summary
Challenge **Theory-of-Everything** from the Pwny-CTF CTF, misc category. Main technique: jail-escape. Reflex character filter + exec(bytes): think about source encoding declarations.

## Statement and artefacts
Meet the new super pythonic AI who can solve anything you throw at it (sometimes).

`nc chal.sigpwny.com 7005`

**author**: Cameron

```python
allowed = string.ascii_letters + string.digits + string.whitespace + "+-*/=" + "#"
if is_bad(user_input):  # rejects any character other than 'allowed'
    return ...
exec(user_input.encode(), {"e": math.e, "pi": math.pi}, {})
```
Prohibited in raw input: parentheses, quotation marks, periods, underscores, brackets, commas, backslashes... So impossible to write `open(...)` directly. The clue: “another *encoding* could give more characters”.

**Provided files / artifacts:**

## Recognition signals
- Signal: #coding=. (with =) bypasses a filter that blocks:. Line separator \r when we don't have.

## Resolution method
1. **The reasoning**

`exec(user_input.encode())`: the input is encoded (UTF-8) then executed **as source code**. However, Python reads the source code taking into account a possible **encoding declaration** (PEP 263): a comment line like `# coding: <codec>` (or `# coding=<codec>`) at the head of the file changes the codec used to decode all the rest of the source.

The winning codec is **UTF-7**: it encodes arbitrary Unicode characters with a sequence `+<base64>-` which only uses **allowed** characters (base64 = `A-Za-z0-9+/`, start `+`, end `-`). We therefore insert any Python code (parentheses, quotes, periods, etc.).

Details that make this possible:
- **PEP 263 accepts `coding=`** (not just `coding:`). `:` is prohibited by the filter, but `=` is allowed. Hence `#coding=utf-7` (the `-` of `utf-7` is allowed, not the underscore of `utf_7`).
- **`input()` only reads ONE line**, and the encoding declaration must be on a **separate** line from the body. We separate with `\r` (carriage return): it is a line separator for the Python tokenizer, it is in `string.whitespace` (therefore authorized), and `input()` does not stop on it (it stops at `\n`).

## Solve script
Script path: `scripts/solve.py`

## Flag
sigpwny{encodings_are_fun!}

## Lessons and reusable patterns
- Reflex character filter + exec(bytes): think about source encoding declarations.
- #coding=... (with =) bypasses a filter that blocks:. Line separator \r when we don't have
- Recognize: exec/compile on bytes from an.encode(), with a charset filter.
- Script: work/solve.py.
