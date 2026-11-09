---
title: "Prairie-of-Learning"
ctf: "Pwny-CTF"
category: "misc"
difficulty: "Not specified"
points: 300
techniques: ["prng-mt19937", "jail-escape", "pyjail"]
tools: ["netcat", "python"]
keywords: ["Prairie-of-Learning", "Pwny-CTF", "misc", "prng-mt19937", "jail-escape", "pyjail", "netcat", "python"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Python-Jails/Prairie-of-Learning/notes.md"
---

# Prairie-of-Learning (Pwny-CTF, misc)

## Summary
Challenge **Prairie-of-Learning** from the Pwny-CTF CTF, misc category. Main technique: prng-mt19937. Pyjail reflex: when “inaccessible” data is a local variable of a function

## Statement and artefacts
Hey come do my quiz! I bet you can't get a perfect score!

Can you hack my quiz and get a 100%? I'll tell you the flag if you do!

`nc chal.sigpwny.com 7004`

**author**: Pete

A 3-question quiz; it takes 3/3 for the server to display the flag.
- Q1: `1+2` → response `3` (clearly in the code).
- Q2: regex for strings containing `000` → response `(0+1)*000(0+1)*` (in plain text).
- Q3: “guess the number between 1 and 99999999 that I think” → a `random.randint` stored in the **local** variable `quiz_question_answer`, then:
  ```python
  sys.stdout, sys.stderr, original_stdout = StringIO(), StringIO(), sys.stdout  # we cut the output
  n = eval(input(''), {}, {})       # our entry is evaluated
  if n == quiz_question_answer: score += 1
  ```

**Provided files / artifacts:**

## Recognition signals
- Signal: Pyjail reflex: when “inaccessible” data is a local variable of a function.

## Resolution method
1. **The reasoning**

We can't guess the `random`. But our entry goes through `eval(..., {}, {})`. Two important points:
1. **`eval(expr, {}, {})`: the provided globals/locals are empty, but Python automatically re-injects `__builtins__`** as soon as the globals dict does not contain any. So we have access to all the builtins, including `__import__`.
2. **`do_quiz`'s local variables are not in our `eval` scope** — BUT they still exist in `do_quiz`'s *frame*, just above ours in the call stack. `sys._getframe(1)` returns this calling frame, and `.f_locals` is the dict of its local variables.

A *frame* = the “execution form” of a function call (its local variables, where we are). Each call stacks one frame; `sys._getframe(0)` = the current frame (that of `eval`), `sys._getframe(1)` = the one that called = `do_quiz`.

2. **Payload**

```python
__import__('sys')._getframe(1).f_locals['quiz_question_answer']
```
`eval` calculates it → it is exactly worth `quiz_question_answer` → `n == quiz_question_answer` → score 3/3. (Redirecting `sys.stdout` to `StringIO` just prevents printing the flag *directly*; it does not prevent reading the variable.)

## Solve script
Script path: [scripts/solve.py](scripts/solve.py)

## Flag
sigpwny{studying_must_have_paid_off}

## Lessons and reusable patterns
- Pyjail reflex: when “inaccessible” data is a local variable of a function
- eval(expr, {}, {}) is not a sandbox: __builtins__ returns by itself. To actually
- Clues from the platform confirmed the track (sys._getframe).
- Script: work/solve.py.
