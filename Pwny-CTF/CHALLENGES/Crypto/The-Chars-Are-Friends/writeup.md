---
title: "The-Chars-Are-Friends"
ctf: "Pwny-CTF"
category: "crypto"
difficulty: "Not specified"
points: 200
techniques: ["xor-cipher"]
tools: ["python"]
keywords: ["The-Chars-Are-Friends", "Pwny-CTF", "crypto", "xor-cipher", "python", "xor"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Crypto/The-Chars-Are-Friends/notes.md"
---

# The-Chars-Are-Friends (Pwny-CTF, crypto)

## Summary
Challenge **The-Chars-Are-Friends** from the Pwny-CTF CTF, crypto category. Main technique: xor-cipher. **OTP = security only if the key is as long as the message, random, and used once

## Statement and artefacts
I heard one time pads are impossible to break, so I decided to roll my own! This version could even work with a shorter key. Try to unencrypt the flag.

“Homemade” encryption supposed to be a one-time pad:
```python
def hide(c):
    r = ord(os.urandom(1))
    return ord(c) ^ (r & 0xc0)     # XOR with a random byte MASK by 0xc0
```
The clue: “look at what `hide` does: what information is hidden, which is not? »

**Provided files / artifacts:**
- `work/message.txt (text, 280 B)`

## Recognition signals
- Signal: **OTP = security only if the key is as long as the message, random, and used once.
- If we observe Trap: number/letter ambiguity on low bits, remember to remove with the known prefix and the meaning.

## Resolution method
1. **The reasoning**

`0xc0 = 1100_0000`. So `r & 0xc0` only has 1 bits on **positions 6 and 7** (the 2 most significant bits). XOR therefore only modifies these 2 bits: **the 6 least significant bits of the character remain intact** in the cipher. A true OTP must be random on **all** bits; here 6 bits out of 8 leak clear.

However, the characters of a flag are printable ASCII (`a-z A-Z 0-9 _ { }`), all < 128, and their **low 6 bits** are almost enough to identify them. For each byte encrypted `c`: `real_character & 0x3f == c & 0x3f`. There are only 4 possibilities left (the 2 high bits: `00/40/80/c0`). We keep the one that is a **valid flag character**.

For each byte: `low = c & 0x3f`, `{low, low|0x40, low|0x80, low|0xc0}` candidates, we choose the printable candidate of the charset flag. Some positions are ambiguous between a **digit** and a **letter** (e.g. `3`/`s` share the low bits): the structure `sigpwny{...}` and the English words contrast (we prefer the letter/symbol). Result:
```
```

## Solve script
Script path: [scripts/my-solve.py](scripts/my-solve.py)
Script path: [scripts/solve.py](scripts/solve.py)
Script path: [scripts/test.py](scripts/test.py)
Script path: [scripts/the_chars_are_friends.py](scripts/the_chars_are_friends.py)

## Flag
sigpwny{random_isnt_automatically_secure}

## Lessons and reusable patterns
- **OTP = security only if the key is as long as the message, random, and used once
- XOR reflex: look at which bits are actually affected. A mask lets others escape
- Trap: number/letter ambiguity on low bits -> raise with the known prefix and the meaning.
- Script: work/solve.py.
