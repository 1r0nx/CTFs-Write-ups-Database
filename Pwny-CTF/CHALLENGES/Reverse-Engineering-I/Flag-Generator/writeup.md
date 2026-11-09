---
title: "Flag-Generator"
ctf: "Pwny-CTF"
category: "reverse"
difficulty: "Not specified"
points: 300
techniques: ["reverse-engineering"]
tools: ["python"]
keywords: ["Flag-Generator", "Pwny-CTF", "reverse", "reverse-engineering", "python"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Reverse-Engineering-I/Flag-Generator/notes.md"
---

# Flag-Generator (Pwny-CTF, reverse)

## Summary
Challenge **Flag-Generator** from the Pwny-CTF CTF, reverse category. Main technique: reverse-engineering. A reverse challenge can be "broken" just by performance, not by logic: if a provided script seems correct but never finishes, first look for an algorithmic flaw (cacheless recursion, avoidable quadratic loop, etc.) before doubting the formula itself.

## Statement and artefacts
Just created my own flag generator in python! Just run it to get the flag!

...find how to get the flag.

**author**: Pete

**Provided files / artifacts:**

## Recognition signals
- Signal: A reverse challenge can be "broken" just by performance, not by logic: if a provided script seems correct but never finishes, first look for an algorithmic flaw (recursion without cache, avoidable quadratic loop, etc.) before doubting the formula itself.

## Resolution method
1. Read `magic.py`: `magic(n) = 1` if `n == 0`, otherwise `Σ magic(i) * magic(n-i-1)` for `i` from `0` to `n-1`. Running as is never ends (explosion in the number of recursive calls).
2. Follow the clues: “current algorithm” + “search for the continuation on OEIS”. By typing the first values ​​(`1, 1, 2, 5, 14, 42…`), we recognize the **Catalan numbers** — exactly the recurrence formula of the code.
3. The real problem is **not** the logic (already correct) but the performance: `magic(i)` is recalculated from zero on each call, for each subterm of each sum → **memorizing** with `@functools.lru_cache(maxsize=None)` on `magic()` is enough so that each value is only calculated once.
4. The flag is `chr(magic(i) - offsets[i])` for each `i` in the provided `offsets` list — this part of the code was already correct, no changes needed.
5. Run the corrected version (`solve.py`) → flag displayed instantly.

## Solve script
Script path: [scripts/magic.py](scripts/magic.py)
Script path: [scripts/solve.py](scripts/solve.py)

## Flag
sigpwny{catatonically_slow_calculation}

## Lessons and reusable patterns
- A reverse challenge can be "broken" just by performance, not by logic: if a provided script seems correct but never finishes, first look for an algorithmic flaw (cacheless recursion, avoidable quadratic loop, etc.) before doubting the formula itself.
- Identify a numerical sequence via OEIS: typing the first 4-5 terms calculated by hand (or via a small script limited to small n) is often enough to find the name of the algorithm sought.
- @functools.lru_cache(maxsize=None): memorization in one line, without touching the logic of the function — the reflex to have as soon as a recursion recalls the same subcases several times (Catalan, naive Fibonacci, etc.).
