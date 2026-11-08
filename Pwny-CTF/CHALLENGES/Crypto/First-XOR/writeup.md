---
title: "First-XOR"
ctf: "Pwny-CTF"
category: "crypto"
difficulty: "Not specified"
points: 50
techniques: ["xor-cipher", "prng-mt19937", "encoding"]
tools: []
keywords: ["First-XOR", "Pwny-CTF", "crypto", "xor-cipher", "prng-mt19937", "encoding", "xor", "hex"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Crypto/First-XOR/notes.md"
---

# First-XOR (Pwny-CTF, crypto)

## Summary
Challenge **First-XOR** from the Pwny-CTF CTF, crypto category. Main technique: xor-cipher. XOR key 1 byte = 256 possibilities -> always bruteforceable. Filter by expected keyword (sigpwny{) or by “readability” (printable characters).

## Statement and artefacts
I mean it's one byte, Michael, how long could it take, *10 seconds*?

Can you decrypt the original message given the encrypted output in "message.txt"?

**Provided files / artifacts:**
- `message.txt (text, 62 B)`
- `req.txt (text, 206 B)`

## Recognition signals
Not specified.

## Resolution method
1. `chal.py`: each byte of the flag is XORed with **the same random byte** (`random.randint(0,255)`), output in **hex** (`message.txt`).
2. Bruteforce the 256 keys and keep the one that gives readable text starting with `sigpwny{`:

```python
   ct = bytes.fromhex(open("message.txt").read().strip())
   for k in range(256):
       out = bytes(b ^ k for b in ct)
       if b"sigpwny{" in out:
           print(hex(k), out); break
   ```

1. (personal: `aletheia xor_brute -s <hex> -l 1 | grep sig`)
3. `key = 0xc1` → `sigpwny{brut3_f0rce_go3s_brrrr}`.

## Flag
sigpwny{brut3_f0rce_go3s_brrrr}

## Lessons and reusable patterns
- XOR key 1 byte = 256 possibilities -> always bruteforceable. Filter by expected keyword (sigpwny{) or by “readability” (printable characters).
- XOR is reversible: (m^k)^k = m. Decrypt = re-apply the same XOR.
- Reflex: convert the hex into bytes (bytes.fromhex) before handling.
