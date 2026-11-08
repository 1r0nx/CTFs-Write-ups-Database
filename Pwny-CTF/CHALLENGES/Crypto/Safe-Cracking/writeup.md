---
title: "Safe-Cracking"
ctf: "Pwny-CTF"
category: "crypto"
difficulty: "Not specified"
points: 200
techniques: ["diffie-hellman"]
tools: ["netcat", "python"]
keywords: ["Safe-Cracking", "Pwny-CTF", "crypto", "diffie-hellman", "netcat", "python"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Crypto/Safe-Cracking/notes.md"
---

# Safe-Cracking (Pwny-CTF, crypto)

## Summary
Challenge **Safe-Cracking** from the Pwny-CTF CTF, crypto category. Main technique: diffie-hellman. Main pitfall (workflow): nc host port in the statement ⟹ the result of my calculations is

## Statement and artefacts
We found a magical safe. There are apparently many valuable items in it such as an invisibility cloak, an Amazon giftcard, and more! Can you please help us recover the original combination?

`nc chal.sigpwny.com 1991`

**author**: Sophia

Three small problems; everyone's answer is a **part of the combination** of the chest.

**Provided files / artifacts:**
- `work/note.txt (text, 731 B)`

## Recognition signals
- Signal: Main trap (workflow): nc host port in the statement ⟹ the result of my calculations is.

## Resolution method
1. **Resolution (DH reminders: public g, p; private a; public A=g^a; secret s=g^(ab)=A^b=B^a)**

1. `p=17, g=3`, Anna private `5`, Beatrice private `11`. **Shared secret** = `g^(a·b) = 3^(5·11) mod 17 = 11`.
2. `p=157, g=2`, Anna private `67`. **Anna's public key** = `g^67 mod 157 = 112`.
3. `p=3042161, g=5`, secret `s=2417097`, private Beatrice `73`. **Anna's private key** `a`: we have `s = (g^b)^a mod p`, therefore basic discrete log `g^73`. `p` small → brute force → `a = 81`.

Combination = **11, 112, 81**. ⚠️ This is **not** the flag: the description gives `nc chal.sigpwny.com 1991`. The combination is the **code to type in the remote trunk**; it is the **server** which returns the real `sigpwny{...}` once the correct code is given. (Trap experienced: 6 attempts refused by submitting `11_112_81` in all formats to CTFd.)

## Solve script
Script path: `scripts/solve.py`

## Flag
sigpwny{is_this_r3@lly_the_m0st_s3cure_s@f3_3ver?}

## Lessons and reusable patterns
- Main pitfall (workflow): nc host port in the statement ⟹ the result of my calculations is
- Know how to distinguish the 3 DH calculations: public = g^priv, secret = pub_other^priv = g^(ab),
- s = B^a: find a = discrete log base B (Beatrice's public key), not base g.
- Script: work/solve.py.
