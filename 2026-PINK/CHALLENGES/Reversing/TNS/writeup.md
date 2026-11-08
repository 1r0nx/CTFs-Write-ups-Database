---
title: "TNS"
ctf: "2026-PINK"
category: "reverse"
difficulty: "Not specified"
points: 25
techniques: ["substitution-cipher"]
tools: []
keywords: ["TNS", "PINK", "reverse", "substitution-cipher", "zip", "https", "got"]
status: "solved"
has_script: false
source: "PINK/CHALLENGES/Reversing/TNS/notes.md"
---

# TNS (PINK, reverse)

## Summary
Challenge **TNS** from the PINK CTF, reverse category. Main technique: substitution-cipher..tns are TI-Nspire documents: a ZIP type container with a proprietary header. They contain Lua scripts (pink.py, lib_pink.py) stored in standard deflate. The pink.py script contains a numeric cipher; each number is an index in a 65-character permutation defined in lib_pink.py.

## Statement and artefacts
I really like my calculator... en:/

- Header: `*TIMLP0900` (10 bytes).
- The first ZIP file starts at offset `0x0a` **without signature `PK\x03\x04`**; the following ones have a normal local signature.
- Local/central headers are in classic ZIP (little-endian) format.
- No EOCD record (`PK\x05\x06`): The file ends with the central directory.

| file | role |
|---------|------|
| `work/pink.tns` | main document (contains `pink.py`, `pink.pyt`) |
| `work/lib_pink.tns` | library (contains the alphabet) |

No auxiliary script has been kept: extraction and decoding take just a few lines of Python (in the method).

**Provided files / artifacts:**
- `work/lib_pink.tns (document TI-Nspire, 1.5 KB)`
- `work/pink.tns (document TI-Nspire, 1.5 KB)`

## Recognition signals
Not specified.

## Resolution method
1. **pink.tns**

| entrance | method | comp. | decomp. |
|--------|---------|-------|---------|
| `Document.xml` | 13 (TI) | 518 | 1174 |
| `Problem1.xml` | 13 (TI) | 331 | 712 |
| `pink.pyt` | 8 (deflate) | 119 | 158 |
| `pink.py` | 8 (deflate) | 203 | 313 |

2. **lib_pink.tns**

| entrance | method | comp. | decomp. |
|--------|---------|-------|---------|
| `Document.xml` | 13 (TI) | 518 | 1174 |
| `Problem1.xml` | 13 (TI) | 266 | 410 |
| `lib_pink.py` | 8 (deflate) | 419 | 797 |

Methods 13 (`Document.xml`, `Problem1.xml`) are not necessary for the flag: Lua scripts are in standard deflate and decompress with `zlib.decompress(data, -15)`.

3. **Extract**

```python
import zlib

# pink.tns
b = open('work/pink.tns', 'rb').read()
pink_py = zlib.decompress(b[1133:1133+203], -15)   # pink.py
pink_pyt = zlib.decompress(b[977:977+119], -15)    # pink.pyt

# lib_pink.tns
b = open('work/lib_pink.tns', 'rb').read()
lib_pink = zlib.decompress(b[915:915+419], -15)    # lib_pink.py
```

> Data offsets come from local headers: `dataoff = offset_local + 30 + nom + extra`. Sizes are in local/central headers.

4. **lib_pink.py**

```python
alphabet = "jXOsE_Q7YB32KVqRGFUx15IcltpCNg8{HMz49baWkiTud60vmhnLAoSZDyewr}PJf"
def get(list): 
  if list == "alphabet": return alphabet
#hi
#this is my lib
#do you like it
#I randomly generated a list
#pls say that you are liking it:)
...
#nothing here btw lol
...
#ok u knew but here you go:
#https://www.youtube.com/watch?v=E4WlUXrJgy4
...
#what do you want here you got your stuff!
...
#sh*t you were to good:(
#\u0062\u0022\u0028\u0012\u0031\u0004\u0033\u0025\u0053...
```

- The alphabet is a **permutation of 65 characters** (subscripts `0..64`).
- The comments are decoys; the YouTube link is a **rickroll** (`E4WlUXrJgy4` = Rick Astley – *Never Gonna Give You Up*).
- The last line `#\u0062...` is an obsolete/decoy escaped Unicode string, useless for decoding.

5. **pink.py**

```python
import lib_pink as pinkctf
e = pinkctf.get("alphabet")
c = "62 22 28 12 31 0 43 3 25 5 35 5 3 20 48 26 24 10 5 26 60 46 29 60 35 48 5 20 5 59 60 46 25 10 5 46 50 5 48 57 5 50 10 59 5 23 35 24 23 43 24 35 25 46 60 61"
f = ""
for n in c.split():
    f += e[int(n)]
print(f)
```

`pink.pyt` is a variant that asks the user for the cipher (same logic), without the hardcoded cipher.

6. **Decoding**

Each number in the cipher is an index in `alphabet`:

```python
e = "jXOsE_Q7YB32KVqRGFUx15IcltpCNg8{HMz49baWkiTud60vmhnLAoSZDyewr}PJf"
c = "62 22 28 12 31 0 43 3 25 5 35 5 3 20 48 26 24 10 5 26 60 46 29 60 35 48 5 20 5 59 60 46 25 10 5 46 50 5 48 57 5 50 10 59 5 23 35 24 23 43 24 35 25 46 60 61"
print(''.join(e[int(n)] for n in c.split()))
```

Result:

```
```

Remarkable matches: `62 → P`, `22 → I`, `28 → N`, `12 → K`, `31 → {`, `61 → }` → valid flag structure and sentence consistent with the statement.

## Flag
PINK{just_4_s1mpl3_pr0gr4m_1_wr0t3_0n_my_n3w_c4lcul4t0r}

## Lessons and reusable patterns
- Main technique: substitution-cipher.
