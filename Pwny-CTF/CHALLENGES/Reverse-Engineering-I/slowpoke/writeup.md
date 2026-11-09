---
title: "slowpoke"
ctf: "Pwny-CTF"
category: "reverse"
difficulty: "Not specified"
points: 300
techniques: ["reverse-engineering"]
tools: ["python"]
keywords: ["slowpoke", "Pwny-CTF", "reverse", "reverse-engineering", "python"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Reverse-Engineering-I/slowpoke/notes.md"
---

# slowpoke (Pwny-CTF, reverse)

## Summary
Challenge **slowpoke** from the Pwny-CTF CTF, reverse category. Main technique: reverse-engineering. Rolling hash h = h*31 + ord(c): invertible as soon as we have the intermediate hashes. Each character = (h_i - h_{i-1}*31) mod 2^n. Recognize this pattern (multiplication by a small constant + addition of byte) = never brute-force.

## Statement and artefacts
There are almost enough numbers to make this a crypto chal.

**Author**: Richard

**Provided files / artifacts:**

## Recognition signals
- Signal: time.sleep in a check function = signal that the expected channel is a slow brute-force; seek a direct reversal rather than endure it (hence "slowpoke").

## Resolution method
1. Read `main.py`: the flag (25 char. = `len(correct)`) is passed in `shuffle()`, then for each prefix `hash(flag[:i+1])` is compared to `correct[i]`.
2. Observe that `hash` is a **rolling hash**: `h0 = 0x60e647a3`, `h_i = (h_{i-1}*31 + ord(c_i)) & 0xffffffff`. So `correct[i]` = hash of the first mixed `i+1` characters, and each `correct[i]` derives from `correct[i-1]` by a single character.
3. Reverse step by step: `ord(c_i) = (correct[i] - prev*31) & 0xffffffff` (where `prev = correct[i-1]`, and `h0` for the first). This gives the flag in **mixed** order (`pt_}r{y3vt7yryirn3_3slegw`).
4. Reverse the `shuffle`: it is **deterministic** (global seed = 0, `randint` does not depend on the content) → replaying it on `list(range(25))` gives the permutation `perm` (original index at each position). Rebuild: `orig[perm[i]] = shuffled[i]`.
5. Result: `sigpwny{try_3v3ry_l3t7er}` — the flag name describes the *intended* solution (letter-by-letter brute-force), which direct inversion makes useless.

## Solve script
Script path: [scripts/solve.py](scripts/solve.py)

## Flag
sigpwny{try_3v3ry_l3t7er}

## Lessons and reusable patterns
- Rolling hash h = h*31 + ord(c): invertible as soon as we have the intermediate hashes. Each character = (h_i - h_{i-1}*31) mod 2^n. Recognize this pattern (multiplication by a small constant + addition of byte) = never brute-force.
- time.sleep in a check function = signal that the expected channel is a slow brute-force; seek a direct reversal rather than endure it (hence "slowpoke").
- Deterministic permutation independent of content (Fisher-Yates with fixed seed): no need to understand the algorithm, replaying it on range(n) gives the order, which is then reversed. (Challenge clues: “figure out the shuffle order without understanding shuffle” + “every flag character is checked independently”.)
- Two stacked obfuscations (hash + shuffle) are handled separately: first get the shuffled list, then put it back in order.
