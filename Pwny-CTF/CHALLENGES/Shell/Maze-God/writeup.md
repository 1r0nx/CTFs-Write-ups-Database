---
title: "Maze-God"
ctf: "Pwny-CTF"
category: "misc"
difficulty: "hard"
points: 500
techniques: []
tools: ["pwntools", "netcat", "python"]
keywords: ["Maze-God", "Pwny-CTF", "misc", "pwntools", "netcat", "python"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Shell/Maze-God/notes.md"
---

# Maze-God (Pwny-CTF, misc)

## Summary
Challenge **Maze-God** from the Pwny-CTF CTF, misc category. “god” challenge / N rounds = scripting challenge: automate reading + response (pwntools: remote, recvuntil, recvline, sendline).

## Statement and artefacts
Another god challenge, can you solve 1000 mazes before time runs out?!

`nc chal.sigpwny.com 3502`

Service `nc chal.sigpwny.com 3502`: you must solve **1000 mazes** before time runs out. `server.py` provided gives the exact protocol.

**Provided files / artifacts:**
- `Dockerfile (file, 238 B)`

## Recognition signals
Not specified.

## Resolution method
1. **Protocol (read in server.py)**

- 1000 rounds. Each turn: `gen_maze(16,16)` → grid **18×18** (border `#`), agent `o` in `(1,1)`, exit `E` in `(15,15)`.
- Display:
  ```
  <<< Maze i
   <18 lines, each prefixed with a SPACE>
               End >>>
  ```
- Expected response: a series of moves `L R U D` (Left/Right/Up/Down), **1 square per move**, validated by `check_solution` (forbidden to cross `#`, must end on `E`).

1. **Validate the BFS locally** with `gen_maze`/`check_solution` of the server (de-risking) → 200/200.
2. **Network solver** (`solve.py`, pwntools): for each maze, `recvuntil("<<< Maze")`, read 18 lines (remove leading space), BFS from `o` to `E`, `sendline` from the solution.
3. After 1000 passes → the flag.

2. **More difficult variation**

- Very tight time → optimize (keep the connection, avoid `sleep`, batch readings).
- Larger noisy/maze input format → robust parsing + BFS/A*.

## Solve script
Script path: `scripts/server.py`
Script path: `scripts/solve.py`

## Flag
sigpwny{th3s3u5_b3at_de@da1us_gG}

## Lessons and reusable patterns
- “god” challenge / N rounds = scripting challenge: automate reading + response (pwntools: remote, recvuntil, recvline, sendline).
- Parsing: each line of the maze is prefixed with a space (print(" " + line)) -> remove 1 lead tank.
- Algo: perfect maze (Prim) -> BFS (shortest path) on non-# squares, reconstruct the path in moves.
- Always test the algorithm locally before burning tests on the server.
