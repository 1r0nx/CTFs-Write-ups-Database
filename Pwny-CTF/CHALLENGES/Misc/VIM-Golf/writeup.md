---
title: "VIM-Golf"
ctf: "Pwny-CTF"
category: "misc"
difficulty: "Not specified"
points: 200
techniques: ["encoding"]
tools: ["netcat", "bash", "python"]
keywords: ["VIM-Golf", "Pwny-CTF", "misc", "encoding", "netcat", "bash", "python", "hex"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Misc/VIM-Golf/notes.md"
---

# VIM-Golf (Pwny-CTF, misc)

## Summary
Challenge **VIM-Golf** from the Pwny-CTF CTF, misc category. Main technique: encoding. VIM macro = loop: qq … q records, N@q replays N times. Ideal for

## Statement and artefacts
Fewer characters are better in this epic VIM Golf! Can you get under 40 keys?

`nc chal.sigpwny.com 5092`

**author**: richard

**Provided files / artifacts:**

## Recognition signals
Not specified.

## Resolution method
1. **The idea**

Reproduce in VIM a `out.txt` file of 9 lines “N hello” (N=1..9) in a **minimum number of keystrokes**. We record the keystrokes (`-W recording.bin`), submit the hex to the server (`nc chal.sigpwny.com 5092`), which replays them (`-s`) and compares `out.txt`.

2. **Solution (30 keystrokes)**

```
i1 hello<Esc>     " insert the first line "1 hello"
qq                " starts recording macro q
Yp                " Y=yy (duplicate the line), p (paste below)
<Ctrl-A>          " increments the 1st number in the line (1->2)
q                 " end of the macro (we now have 2 lines)
7@q               " replays the macro 7x -> lines 3..9
:wq out.txt<CR>   " writes the buffer to out.txt and exits
```
Hex to submit: `69312068656c6c6f1b7171597001713740713a7771206f75742e7478740d`

## Solve script
Script path: [scripts/chal.sh](scripts/chal.sh)
Script path: [scripts/solve.py](scripts/solve.py)

## Flag
sigpwny{v1m_i5_qu17e_c0mp4c7}

## Lessons and reusable patterns
- VIM macro = loop: qq … q records, N@q replays N times. Ideal for
- Ctrl-A increments the number below/after the cursor (and Ctrl-X decrements):
- :wq {file} writes the current buffer to a named file then exits.
- Count in bytes: each keystroke = 1 byte (including Esc=0x1b, Ctrl-A=0x01,
