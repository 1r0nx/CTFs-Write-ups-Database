---
title: "More-Hash-More-Better"
ctf: "Pwny-CTF"
category: "crypto"
difficulty: "Not specified"
points: 100
techniques: ["prng-prediction"]
tools: ["python"]
keywords: ["More-Hash-More-Better", "Pwny-CTF", "crypto", "prng-prediction", "python", "ecb"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Crypto/More-Hash-More-Better/notes.md"
---

# More-Hash-More-Better (Pwny-CTF, crypto)

## Summary
Challenge **More-Hash-More-Better** from the Pwny-CTF CTF, crypto category. Main technique: prng-prediction. Hash character by character = ECB of hash: each character always gives the same hash -> trivial bruteforce/table, regardless of the number of iterations.

## Statement and artefacts
I heard one way hash functions are super secure. I bet if I use it many times it'll be even more secure.

Can you determine the input flag given the output of the program in "hashes.txt"?

**Provided files / artifacts:**
- `hashes.txt (text, 1.8 KB)`

## Recognition signals
- Signal: hashes.txt = one hash line per flag character.
- Signal: The charset is known and small (a-zA-Z0-9{}_, ~64 characters).
- Signal: A hash is only safe if the input space is large (salt + long/unpredictable inputs). Small known space -> broken.

## Resolution method
1. **Build a table** `sha256(c) -> c` for each possible character in the charset.
2. For each line of `hashes.txt`, find the corresponding character, and concatenate.
   ```python
   import hashlib
   charset="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUV{}0123456789_"
   hashes=[l.strip() for l in open("../hashes.txt")]
   flag="".join(c for h in hashes for c in charset if hashlib.sha256(c.encode()).hexdigest()==h)
   print(flag)
   ```
3. → `sigpwny{H45hbr0wn5_4r3_t45ty}`.

1. **The trap (chal.py)**

```python
for c in flag:
    print(sha256(c).hexdigest())   # ONE SHA-256 hash PER character
```
→ `hashes.txt` = one hash line per flag character. The charset is **known and small** (`a-zA-Z0-9{}_`, ~64 characters).

## Solve script
Script path: [scripts/solve.py](scripts/solve.py)

## Flag
sigpwny{H45hbr0wn5_4r3_t45ty}

## Lessons and reusable patterns
- Hash character by character = ECB of hash: each character always gives the same hash -> trivial bruteforce/table, regardless of the number of iterations.
- A hash is only safe if the input space is large (salt + long/unpredictable inputs). Small known space -> broken.
- Recognize: output = several hashes of fixed length, one per symbol -> lookup table attack.
