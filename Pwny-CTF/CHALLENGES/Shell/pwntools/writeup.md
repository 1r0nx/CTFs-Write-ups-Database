---
title: "pwntools"
ctf: "Pwny-CTF"
category: "misc"
difficulty: "Not specified"
points: 75
techniques: []
tools: ["pwntools", "netcat", "python"]
keywords: ["pwntools", "Pwny-CTF", "misc", "netcat", "python"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Shell/pwntools/notes.md"
---

# pwntools (Pwny-CTF, misc)

## Summary
Challenge **pwntools** from the Pwny-CTF CTF, misc category. The pwntools challenge (Pwny-CTF, misc) is documented by a resolution note.

## Statement and artefacts
Can you use your scripting skills to guess all the magic words?

`nc chal.sigpwny.com 5050`

`nc chal.sigpwny.com 5050`: you have to give **100 “magic words”** in a row (too many to do by hand). When you make a mistake, the server **reveals the correct word** (`WRONG WORD! the word was X`) then **cuts the connection**.

**Provided files / artifacts:**
- `Dockerfile (file, 279 B)`
- `magic_words.txt (text, 672 B)`

## Recognition signals
- Signal: remote() in the loop = a new connection each turn (the server starts from scratch). Open it once per attempt, not in a tight loop.
- If we observe Empty file, think of for w in [] never executes -> think of starting the 1ᵉʳ word.
- Signal: Do not probe the next word -> you never discover anything new. After the known ones, send a decoy.
- Signal: Parsing a word with space: the word was ad hoc -> split(" ")[-1] gives hoc (false!). Use split("the word was ", 1)[1].strip().
- If we look at file.write(word) without \n, think about the words sticking together. Write word + “\n”.
- Signal: EOFError on sendlineafter = the socket is closed (bad word replayed -> Goodbye, or flag already given): there is no longer a prompt to wait for.

## Resolution method
1. **Strategy (incremental learning)**

You can only learn **one** word per connection (the server closes after an error). So:
1. Replay **all words already known** (stored in `magic_words.txt`).
2. At the next (unknown) position, send a **decoy** (`...`) → read `the word was X` → **add X** to the file.
3. Reconnect and start again until you get the flag (`sigpwny` in the response).

2. **Skeleton (pwntools)**

```python
from pwn import remote
words = [l.strip() for l in open("magic_words.txt") if l.strip()]
io = remote("chal.sigpwny.com", 5050)
for w in words:
    io.sendlineafter(b"word? ", w.encode())     # replay the known
io.sendlineafter(b"word? ", b"...")             # probe the next
res = io.recvline()
new = res.decode().split("the word was ", 1)[1].strip()   # extract the word
open("magic_words.txt","a").write(new + "\n")
```

3. **Pitfalls encountered (⚠️ to remember)**

- **`remote()` in the loop** = a new connection each turn (the server starts from scratch). Open it **once per attempt**, not in a tight loop.
- **Empty file** → `for w in []` never executes → remember to start the 1st word.
- **Do not probe the next word** → we never discover anything new. After the known ones, send a decoy.
- **Parsing a word with space**: `the word was ad hoc` → `split(" ")[-1]` gives `hoc` (false!). Use `split("the word was ", 1)[1].strip()`.
- **`file.write(mot)` without `\n`** → the words stick together. Write `mot + "\n"`.
- **`EOFError`** on `sendlineafter` = the socket is **closed** (bad word replayed → Goodbye, or flag already given): there is no more prompt to wait for.

## Solve script
Script path: `scripts/dist.py`
Script path: `scripts/solve.py`

## Flag
sigpwny{this_makes_me_feel_like_a_bot}

## Lessons and reusable patterns
Not specified.
