---
title: "PM-Hash"
ctf: "Pwny-CTF"
category: "forensics"
difficulty: "Not specified"
points: 150
techniques: ["hash-collision", "encoding"]
tools: ["python"]
keywords: ["PM-Hash", "Pwny-CTF", "forensics", "hash-collision", "encoding", "python", "hex", "got"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Forensics/PM-Hash/notes.md"
---

# PM-Hash (Pwny-CTF, forensics)

## Summary
Challenge **PM-Hash** from the Pwny-CTF CTF, forensics category. Main technique: hash-collision. Design flaw: chopping in independent blocks breaks the “avalanche” effect of a real hash. The cost goes from “impossible” (94^18) to “18 × 94² tries” because the blocks are solved one by one.

## Statement and artefacts
I got so excited learning about the state-of-the-art LM hash, I designed my own algorithm, PM hash based on it. I'm sure it's unbreakable. Here's the hash of my password:

`9272c1d1f611c71643a9d5a59109feb9c51c03c7`

Here is the Python script I used to generate the hash:
```
import hashlib
password = '???'
def hash_password(password):
  hash = ''
  for i in range(0, len(password), 2):
    chunk = password[i:i+2]
    # Don't ask me why I chose 4, it just felt right
    hash_bit = hashlib.md5(chunk.encode()).hexdigest()[:4]
    hash += hash_bit
  return hash

print(hash_password(password))
```

**Author**: Pete

## Recognition signals
Not specified.

## Resolution method
1. The target hash is 40 hex characters long. It is in reality the concatenation of blocks of **4 hexes**, each block = `md5(2 characters)[:4]` (the first 4 hexes of the MD5 of a pair of characters).
2. As each pair of characters only depends on its own block, we **precompute a table**: for all possible pairs (94×94), store `md5(pair)[:4] → pair`.
3. For each block of 4 hexes of the target, find the candidate pairs in the table (manage the last block of 1 character if odd length).
4. Recombine the candidates and recheck the full hash → password `i_l0vE_blAckbeRr13s`.

## Solve script
Script path: `scripts/hasher.py`
Script path: `scripts/solve.py`

## Flag
i_l0vE_blAckbeRr13s

## Lessons and reusable patterns
- Design flaw: chopping in independent blocks breaks the “avalanche” effect of a real hash. The cost goes from “impossible” (94^18) to “18 × 94² tries” because the blocks are solved one by one.
- Recognize this type: hash length = multiple of the length of a md5(small_piece)[:k], or source code showing a loop that hashes piece by piece.
- Truncating an MD5 to 4 hexes creates collisions (several pairs -> same block): hence the final step of re-verifying the complete hash to remove the ambiguity.
- itertools.product(CHARSET, repeat=2) = all pairs; string.printable[:94] = numbers + letters + punctuation (probable password charset).
