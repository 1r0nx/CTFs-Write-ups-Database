---
title: "Password-Cracking"
ctf: "Pwny-CTF"
category: "crypto"
difficulty: "Not specified"
points: 150
techniques: ["password-cracking", "encoding", "hash-cracking"]
tools: ["john", "hashcat"]
keywords: ["Password-Cracking", "Pwny-CTF", "crypto", "encoding", "hash-cracking", "john", "hashcat", "hex"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Crypto/Password-Cracking/notes.md"
---

# Password-Cracking (Pwny-CTF, crypto)

## Summary
Challenge **Password-Cracking** from the Pwny-CTF CTF, crypto category. Main technique: password-cracking. “Decrypt a hash” = misnomer: SHA-256 is one-way. We can only guess + re-hash + compare.

## Statement and artefacts
We successfully obtained a SHA-256 hash of a password...all we need to do now is to decrypt it.

**author**: Sophia

**Provided files / artifacts:**
- `hash.txt (text, 64 B)`
- `wordlist.txt (text, 1.5 KB)`

## Recognition signals
- Signal: Dictionary attack when a wordlist is provided; rockyou + rules/mask when the list is not given.
- Signal: Trap:.strip() the lines (the \n changes the hash). The flag here wraps the word in sigpwny{} (the hint "flag = decrypted password" spoke of the word).

## Resolution method
1. `hash.txt` = `0cdff644...151bdc75` (64 hex = SHA-256). `wordlist.txt` = 94 candidate passwords.
2. For each word: `sha256(mot).hexdigest()` == target hash?

```python
   target = open("hash.txt").read().strip()
   for w in open("wordlist.txt"):
       if hashlib.sha256(w.strip().encode()).hexdigest() == target:
           print(w.strip()); break     #-> cr@ckitnow!26
   ```

1. (or `hashcat -m 1400 -a 0 hash.txt wordlist.txt`)
3. Word found: `cr@ckitnow!26` → flag = `sigpwny{cr@ckitnow!26}`.

## Discarded approaches
```bash
# Python (dictionary)
python3 -c 'import hashlib;t=open("hash.txt").read().strip();[print(w.strip()) for w in open("wordlist.txt") if hashlib.sha256(w.strip().encode()).hexdigest()==t]'
# hashcat (SHA-256 = mode 1400)
hashcat -m 1400 -a 0 hash.txt wordlist.txt --show
# john
john --format=raw-sha256 --wordlist=wordlist.txt hash.txt && john --show --format=raw-sha256 hash.txt
```

## Flag
sigpwny{cr@ckitnow!26}

## Lessons and reusable patterns
- “Decrypt a hash” = misnomer: SHA-256 is one-way. We can only guess + re-hash + compare.
- Dictionary attack when a wordlist is provided; rockyou + rules/mask when the list is not given.
- Trap:.strip() the lines (the \n changes the hash). The flag here wraps the word in sigpwny{} (the hint "flag = decrypted password" spoke of the word).
