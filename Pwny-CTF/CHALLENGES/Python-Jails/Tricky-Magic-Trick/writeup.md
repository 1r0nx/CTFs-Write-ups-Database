---
title: "Tricky-Magic-Trick"
ctf: "Pwny-CTF"
category: "misc"
difficulty: "Not specified"
points: 300
techniques: ["prng-mt19937", "reverse-engineering", "jail-escape"]
tools: ["netcat", "python"]
keywords: ["Tricky-Magic-Trick", "Pwny-CTF", "misc", "prng-mt19937", "reverse-engineering", "jail-escape", "netcat", "python"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Python-Jails/Tricky-Magic-Trick/notes.md"
---

# Tricky-Magic-Trick (Pwny-CTF, misc)

## Summary
Challenge **Tricky-Magic-Trick** from the Pwny-CTF CTF, misc category. Main technique: prng-mt19937. Reflex: when compile() is followed by.replace(co_consts=..., co_names=...), disassemble

## Statement and artefacts
Get ready to be a real magician and pull my card out of your hat.

`nc chal.sigpwny.com 7007`

**author**: Cameron

```python
num = random.randint(100, 1000)
print(f"Oops I dropped my card! {num}")        #<-- num is PRINTED (we know it!)
guess = input(...)
answer = compile(guess, "", "eval").replace(co_consts=tuple(range(0,1001)), co_names=())
if eval(answer, {"__builtins__": {}}) == num:   # it is necessary that eval == num
    print(flag)
```

**Provided files / artifacts:**
- `work/Dockerfile (file, 280 B)`

## Recognition signals
- Signal: Reflex: when compile() is followed by.replace(co_consts=., co_names=.), disassemble.

## Resolution method
1. **The reasoning**

We compile our expression, then `.replace(...)`:
- **`co_consts = (0,1,2,...,1000)`**: the constants table is overwritten by `range(0,1001)`. As a result, each `LOAD_CONST i` instruction no longer loads *our* literal, but `co_consts[i] = i` (**the loaded value = the index**).
- **`co_names = ()`**: no usable name/attribute anymore, and `{"__builtins__": {}}` → no builtins.

So: no functions, no attributes; we only have operations and constants whose value = their index in the table. The goal: to create an expression that is exactly `num` (known, because it is printed). We must therefore bring a `LOAD_CONST` of **index `num`** to be the result.

Indices are assigned by **order of first appearance** of constants in the source (deduplicated). Optimizer pitfalls (constant folding) to avoid:
- `[0,1,2]` / `(0,1,2)`: folded into **one** constant tuple (then `LIST_EXTEND`) → breakage on remap.
- `{0:1,2:3}` (multiple constant keys): `BUILD_CONST_KEY_MAP` (folded key table) → case.
- `0+1`, `0 and 1`, `(0,1)[1]`: arithmetic/constant indexing folded at compile time.

**What is NOT folded**: a **comparison chain** `0<1<2<...` (emits an integer `LOAD_CONST`, never folded) and a **one-pair dict** `{k:v}` (opcode `BUILD_MAP`, individual `LOAD_CONST`).

## Solve script
Script path: `scripts/solve.py`

## Flag
sigpwny{what_even_is_a_constant}

## Lessons and reusable patterns
- Reflex: when compile() is followed by.replace(co_consts=..., co_names=...), disassemble
- Constant folding: constant lists/tuples/dicts and constant arithmetic are folded
- Recognize: a displayed (or guessable) random + a transformation of the compiled code.
- Script: work/solve.py.
