---
title: "Low-Level-Python"
ctf: "Pwny-CTF"
category: "misc"
difficulty: "Not specified"
points: 400
techniques: ["jail-escape", "pyjail", "encoding", "vm-reverse"]
tools: ["netcat", "python"]
keywords: ["Low-Level-Python", "Pwny-CTF", "misc", "jail-escape", "pyjail", "encoding", "vm-reverse", "netcat", "python", "hex"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Python-Jails/Low-Level-Python/notes.md"
---

# Low-Level-Python (Pwny-CTF, misc)

## Summary
Challenge **Low-Level-Python** from the Pwny-CTF CTF, misc category. Main technique: jail-escape. Reflex “bytecode by hand + empty tables”: look for opcodes that do not need

## Statement and artefacts
Wait what you can segfault in python?????

`nc chal.sigpwny.com 7006`

**author**: Cameron

```python
from types import CodeType
def win(): print(open("/flag.txt").read())
bytecode = bytes.fromhex(input("Give me your best python bytecode (in hex): "))
eval(CodeType(0, 0, 0, 0, 0, 0, bytecode, (), (), (), "", "", "", 0, bytes(), bytes()))
```
We control **only** `bytecode` (7th argument). Everything else is frozen: `co_consts=()`, `co_names=()`, `co_varnames=()`, `nlocals=0`, **`co_stacksize=0`**, `co_linetable=b""`, **`co_exceptiontable=b""`**. Purpose: read `/flag.txt` via `win()`.

**Provided files / artifacts:**
- `work/Dockerfile (file, 280 B)`

## Recognition signals
Not specified.

## Resolution method
1. **The 3 locks (and how to lift them)**

1. **Empty tables** (`co_consts`/`co_names`/`co_varnames` = `()`): none `LOAD_CONST`, `LOAD_GLOBAL`, `LOAD_NAME`, `LOAD_FAST` by valid index. We can therefore **neither name `win`, nor make a literal string/number**. → Saving opcode: **`LOAD_LOCALS`** (opcode 87). At the module level, `eval(code)` runs with `f_locals == f_globals`; `LOAD_LOCALS` therefore pushes the **dict of globals**, which contains `win`.
2. **`co_exceptiontable = b""`** (required): impossible to place a `try/except`. So **no exception should be thrown**. We cannot “call all the values ​​of the globals while catching the errors” (calling a str/None raises `TypeError` → eval crashes). → We only call **`win`**. But in `chal.py`, `win` is **the penultimate value** of the globals (defined just before `bytecode`, which is the last). So `win == list(globals().values())[-2]`.
3. **`co_stacksize = 0`** (the “segfault in python”): the value stack has 0 slots allocated, any push writes **out of bounds**. Empirical test: stacking is in fact **tolerated** (datastack slack), EXCEPT that a `CALL` function **Python** places the callee frame **on top** of our OOB stack → upon return, reread the stack = corruption/segfault. → We only make **ONE `CALL`** (that of `win`), and we do not **reuse** the stack afterwards (`RETURN_VALUE` immediately). `win` prints the flag, then the eval exits properly.

## Solve script
Script path: [scripts/solve.py](scripts/solve.py)

## Flag
sigpwny{n0W_7HAT_w4ZNT_5o_b4d}

## Lessons and reusable patterns
- Reflex “bytecode by hand + empty tables”: look for opcodes that do not need
- No exctable = zero tolerated exceptions: you need logic that never raises (here: never
- co_stacksize=0: pushing values often works (slack), but a Python CALL corrupts
- Tooling: pyenv install 3.12.3 to match the Dockerfile; dis.opmap,
- Recognize: we directly provide bytecode/object code, empty frozen tables, stacksize
- Script: work/solve.py. Flag obtained from chal.sigpwny.com:7006.
