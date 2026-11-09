---
title: "First-AES"
ctf: "Pwny-CTF"
category: "crypto"
difficulty: "Not specified"
points: 100
techniques: ["aes-ctr", "xor-cipher", "encoding", "malware-analysis"]
tools: ["python"]
keywords: ["First-AES", "Pwny-CTF", "crypto", "aes-ctr", "xor-cipher", "encoding", "malware-analysis", "aes", "xor", "hex", "ctr", "padding"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Crypto/First-AES/notes.md"
---

# First-AES (Pwny-CTF, crypto)

## Summary
Challenge **First-AES** from the Pwny-CTF CTF, crypto category. Main technique: aes-ctr. The First-AES (Pwny-CTF, crypto) challenge is documented by a resolution note.

## Statement and artefacts
- what happens when i take the counter out of AES CTR mode? Do I still have AES?

**Provided files / artifacts:**
- `AESoutput.txt (text, 673 B)`

## Recognition signals
- If we look at AES-CTR = stream cipher, think about ct = pt XOR keystream, keystream = AES(KEY,0)‖AES(KEY,1)‖….
- Signal: Counter.new(128) is recreated on each call -> starts from 0 -> identical keystream for test and flag.
- Signal: AES does not break; we break the mode/use. Here: reused keystream (fixed counter/IV).
- Signal: Two-time pad: C1 XOR C2 = P1 XOR P2 (the keystream is canceled). With a known plaintext -> we recover the other.
- Signal: Alignment: always from offset 0; XOR only on the common length (the shortest).
- Signal: The \x00 padding of the flag shows the test in plain text (useful hint).

## Resolution method
1. `AESoutput.txt`: line 1 = `ct_test` (288 B), line 2 = `ct_flag` (48 B).
2. `test` is **known** (in `chal.py`). Two-time pad:
   ```
   flag = ct_test[:48] XOR ct_flag XOR test[:48]
   ```
(aligned at the START, along the length of the shortest = 48 B)
3. → `sigpwny{m0m_l0ok!_1_fOuND_tH3_w4y!!!}`

1. **The trap (chal.py)**

```python
KEY = os.urandom(16)                 # fixed key (global)
def encrypt(pt):
    cipher = AES.new(KEY, AES.MODE_CTR, counter=Counter.new(128))  # counter restarts at 0!
    return cipher.encrypt(pt).hex()  #=pt XOR keystream
encrypt(test)   # known test (written in the source)
encrypt(flag)   # same KEY + same counter => SAME keystream
```
- AES-CTR = stream cipher: `ct = pt XOR keystream`, `keystream = AES(KEY,0)‖AES(KEY,1)‖…`
- `Counter.new(128)` is recreated on each call → starts from 0 → **identical keystream** for `test` and `flag`.

2. **To remember / pitfalls**

- **AES does not break**; we break the **mode/use**. Here: reused keystream (fixed counter/IV).
- **Two-time pad**: `C1 XOR C2 = P1 XOR P2` (the keystream is canceled). With a known plaintext → we recover the other.
- **Alignment**: always from offset 0; XOR only on the **common length** (shortest).
- The **`\x00` padding** of the flag shows `test` in plain text (useful hint).

## Flag
sigpwny{m0m_l0ok!_1_fOuND_tH3_w4y!!!}

## Lessons and reusable patterns
- Main technique: aes-ctr.
