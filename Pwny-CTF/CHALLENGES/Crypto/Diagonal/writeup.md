---
title: "Diagonal"
ctf: "Pwny-CTF"
category: "crypto"
difficulty: "Not specified"
points: 500
techniques: []
tools: ["netcat", "python"]
keywords: ["Diagonal", "Pwny-CTF", "crypto", "netcat", "python"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Crypto/Diagonal/notes.md"
---

# Diagonal (Pwny-CTF, crypto)

## Summary
Challenge **Diagonal** from the Pwny-CTF CTF, crypto category. Control of the input of a black box = we choose it to linearize the unknown. Here M^d of a

## Statement and artefacts
We've tried and failed with horizontal and vertical integration. Hopefully something more angular will catch on.

`nc chal.sigpwny.com 1989`

**author**: Anakin

The server pulls a secret `d` (~`1e9` to `1e10`), lets us **choose** a 3x3 integer matrix `M`, calculates `M^d`, and returns `res = M[0,0]+M[1,1]+M[2,2] + M[0,1]+M[1,2]+M[0,2]` (diagonal + on-diagonals). You have to guess `d`. Hint: “play with matrices, see how the exponent affects the entries.”

**Provided files / artifacts:**

## Recognition signals
Not specified.

## Resolution method
1. **The reasoning**

We have full control of `M`. We want a `M` whose power `M^d` makes `d` appear **linearly**. The **unipotent matrix** (triangular with 1s on the diagonal) is ideal:
```
M = [[1,1,0],
     [0,1,0],
     [0,0,1]]     ⟹     M^d = [[1, d, 0],
                                [0, 1, 0],
                                [0, 0, 1]]
```
(A block of Jordan `[[1,1],[0,1]]^d = [[1, d],[0,1]]`.) The requested amount is then worth `1+1+1 + d + 0 + 0 = d + 3`. So `secret = res - 3`. We submit and obtain `sigpwny{mult1d1m3n510n4l}`.

## Solve script
Script path: `scripts/public.py`
Script path: `scripts/solve.py`
Script path: `scripts/starter.py`

## Flag
sigpwny{mult1d1m3n510n4l}

## Lessons and reusable patterns
- Control of the input of a black box = we choose it to linearize the unknown. Here M^d of a
- Generalization: [[1,1],[0,1]]^d = [[1, d],[0,1]]; with larger blocks we obtain C(d,2),
- (Server code uses numpy object dtype -> exact Python integers, no overflow, so res = d+3
- Script: work/solve.py.
