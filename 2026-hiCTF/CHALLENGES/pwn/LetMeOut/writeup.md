---
title: "LetMeOut"
ctf: "2026-hiCTF"
category: "pwn"
difficulty: "Not specified"
points: null
techniques: ["ssti", "jail-escape", "encoding"]
tools: ["python"]
keywords: ["LetMeOut", "hiCTF", "pwn", "ssti", "jail-escape", "encoding", "python"]
status: "solved"
has_script: true
source: "hiCTF/pwn/LetMeOut/notes.md"
---

# LetMeOut (hiCTF, pwn)

## Summary
Challenge **LetMeOut** from the hiCTF CTF, pwn category. Main technique: ssti. The LetMeOut challenge (hiCTF, pwn) is documented by a resolution note.

## Statement and artefacts
**Provided files / artifacts:**
- `letmeout.zip (archive, 2.7 KB)`

## Recognition signals
- Signal: is_safe_attribute/is_internal_attribute test argument.startswith("_")/("__") on raw, while getattr sees NFKC form.
- Signal: A Tag (created by rich) whose 1st character is a ＿ fullwidth (U+FF3F) + ASCII: raw does not start with _ -> bypass, but str(Tag) NFKC = "__class__" -> getattr succeeds.
- Signal: Grid vs engine: test the payload against the REAL grid (isascii, len, ≤3 letters) AND against Jinja. The non-ASCII must originate in Jinja (escapes), not in the input.
- Signal: Octal \NNN = ASCII encoding without letters (key to the 3-letter trick). \uXXXX only for the 1st fullwidth tank of the bypass.
- Signal: function.__builtins__ (Python 3.10+) gives the builtins dict without going through __globals__["__builtins__"] -> much shorter payload.
- If we observe Relative path (CWD=/flags) to read, remember to avoid encoding "/flags/".

## Resolution method
1. **The 2 clicks for the grid**

1. **Do not send non-ASCII** (blocked by `layout.isascii()`), but the **escaped text** (`＿`, `\163`). Jinja decodes them using **parsing** (after the grid). The **`\NNN`** octal escapes (digits only) encode any byte **without letters** → budget 3 letters = only the **filter name** `rich`.
2. **Underscores/numbers/`/`/`.` are not letters** → literally typeable. The letters of the filter name too. The rest in octal.

2. **Operation string (1 line ≤170, ASCII, 3 letters)**

- Detect the 2 filters (`{{9|NAME}}` → “9” if present); find the **rich** by testing `(9|F)["__str__"|F]["__builtins__"|F]["__name__"]` → “builtins”.
- `(9|RICH)["＿_str__"|RICH]` → Python method `Tag.__str__`; `["＿_builtins__"|RICH]` → **dict builtins** (Python functions expose `.__builtins__`), at **len ~83**.
- **List**: `…[__import__]("os")[listdir](".")` (CWD=/flags) → the 4 names. (~160 tanks)
- **Read**: for each name (relative, short path) `…[open](nom)[read]()` → content; non-decoy = flag. (~150 tanks)
- Dunders accessed in **attribute** (`__str__`, `__builtins__`) = `"＿"` (1st fullwidth tank) + octal remainder + `|RICH`. Non-`_` dict keys/attributes (`__import__`, `os`, `listdir`, `open`, `read`, names) = pure octal (exact ASCII, no bypass).

3. **The bug (SandboxedEnvironment.getitem, jinja2/sandbox.py)**

```
try: return obj[argument]
except (TypeError, LookupError):
    attr = str(argument)                 # NFKC if argument is a Tag -> normalized dunder
    value = getattr(obj, attr)
    if self.is_safe_attribute(obj, argument, value): return value   # tests BRUT argument
```
`is_safe_attribute`/`is_internal_attribute` tests `argument.startswith("_")/("__")` on the **raw**, while `getattr` sees the **NFKC** form. A `Tag` (created by `rich`) whose 1st character is a `＿` fullwidth (U+FF3F) + ASCII: raw does not start with `_` → **bypass**, but `str(Tag)` NFKC = `"__class__"` → `getattr` succeeds.

4. **Pitfalls/to remember**

- **Grid vs engine**: test the payload against the REAL grid (`isascii`, len, ≤3 letters) AND against Jinja. The non-ASCII must originate **in** Jinja (escapes), not in the input.
- **Octal `\NNN`** = ASCII encoding without letters (key to the 3-letter trick). `\uXXXX` only for the 1st fullwidth tank of the bypass.
- **`function.__builtins__`** (Python 3.10+) gives the builtins dict **without** going through `__globals__["__builtins__"]` → much shorter payload.
- **Relative path** (CWD=/flags) to read → avoid encoding "/flags/".
- **NFKC bypass**: reusable on any Jinja sandbox ≤3.1.x where no normalization is done before `is_safe_attribute`, **if** we can inject a non-ASCII key (here via Tag + escapes).

## Solve script
Script path: `scripts/solve.py`

## Flag
hiCTF{__^_^__n0rm4l1z3_b3f0r3_y0u_tru5t__>_<___7e0dc87df5}

## Lessons and reusable patterns
- Main technique: ssti.
