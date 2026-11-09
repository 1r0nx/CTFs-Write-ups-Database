---
title: "Format-Strings-But-Python"
ctf: "Pwny-CTF"
category: "misc"
difficulty: "Not specified"
points: 400
techniques: ["format-string", "jail-escape"]
tools: ["strings", "netcat", "python"]
keywords: ["Format-Strings-But-Python", "Pwny-CTF", "misc", "format-string", "jail-escape", "strings", "netcat", "python", "got"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Python-Jails/Format-Strings-But-Python/notes.md"
---

# Format-Strings-But-Python (Pwny-CTF, misc)

## Summary
Challenge **Format-Strings-But-Python** from the Pwny-CTF CTF, misc category. Main technique: format-string. Str.format is a mini-reading primitive:.attr and [key] allow you to navigate the

## Statement and artefacts
I got fired at my last job because I used printf in C and that got us hacked. Now I'm moving to python to stay safe...

Flag is in an environment variable named FLAG

`nc chal.sigpwny.com 7008`

**author**: Cameron

The flag is in the environment variable `FLAG`. The program adds two "numbers":
```python
class MySpecialNumber:
    def __init__(self, num): self.num = num
    def __repr__(self): return self.num          #<-- returns our BRUTE string
...
expression = "{num1}+{{num2}}".format(num1=num1).format(num2=num2)
print("Here is the expression I will compute:", expression)
```

**Provided files / artifacts:**

## Recognition signals
Not specified.

## Resolution method
1. **The reasoning (key = DOUBLE.format())**

- `"{num1}+{{num2}}".format(num1=num1)`:
  - `{num1}` is replaced by formatted `num1`. Since the class doesn't define `__str__` or `__format__`, Python stumbles upon `__repr__`, which returns **our input string as is**.
  - `{{num2}}` is a literal `{num2}` (`{{`/`}}` are escaped curly braces).
  - Intermediate result: `"<our_string_num1>+{num2}"`.
- `.format(num2=num2)` re-evaluates **this result as a new template**. So if `num1` contains braces `{...}`, they become **format fields** interpreted in this 2nd round.

→ **Injection**: we put a format field in `num1`. Python format strings allow access to **attributes** (`.attr`) and **indexes** (`[key]`). From the object `num2` we go back:

```
num2.__init__            # a class-related method
    .__globals__         # the dict of the globals of the MODULE where the class is defined
    [os]                 # the 'os' key (the os module, imported at the top of chal.py)
    .environ             # os.environ (the mapping of env variables)
    [FLAG]               # the value of FLAG = the flag
```
Note: in a `str.format` field, `[os]` and `[FLAG]` use the **literal** string `'os'` / `'FLAG'` as key (no need for quotes).

2. **Payload**

- 1st number (`num1`): `{num2.__init__.__globals__[os].environ[FLAG]}`
- 2nd number (`num2`): `0`

The `print("Here is the expression...")` then displays `sigpwny{...}+0`. The `+0` comes from the remaining `+{num2}` (→ `repr(num2)` = `0`). No need to go as far as the final calculation.

## Solve script
Script path: [scripts/solve.py](scripts/solve.py)

## Flag
sigpwny{why_are_format_strings_always_vulnerable}

## Lessons and reusable patterns
- str.format is a mini-reading primitive:.attr and [key] allow you to navigate the
- Recognize: user input that ends up passed to.format() (especially a repr/__str__
- Difference with the string C format: no writing (%n), but very powerful reading of objects.
- Script: work/solve.py.
