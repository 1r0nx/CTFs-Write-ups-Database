---
title: "Not-Rough"
ctf: "Pwny-CTF"
category: "crypto"
difficulty: "easy"
points: 400
techniques: ["xor-cipher", "diffie-hellman", "elgamal"]
tools: ["python"]
keywords: ["Not-Rough", "Pwny-CTF", "crypto", "xor-cipher", "diffie-hellman", "elgamal", "python", "aes", "xor"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Crypto/Not-Rough/notes.md"
---

# Not-Rough (Pwny-CTF, crypto)

## Summary
Challenge **Not-Rough** from the Pwny-CTF CTF, crypto category. Main technique: xor-cipher. First smooth (p-1 friable) = DH/ElGamal breakable by Pohlig-Hellman even without exponent

## Statement and artefacts
Modular exponentiation is really hard to do. Fortunately I used a bunch of primes for my modulus so that you have to figure out all of them.

“Modular exponentiation is hard...luckily I used lots of primes for my modulus. » Hint: “Not rough primes = **smooth primes** (vulnerable to certain attacks)”. We have `g, p, A, B` and the flag XORed with the secret DH.

**Provided files / artifacts:**
- `work/chal.txt (text, 798 B)`

## Recognition signals
Not specified.

## Resolution method
1. **The reasoning**

The `gen_prime` of the challenge makes `p` such that `p-1` is the **product of small primes** (p is a “smooth” prime). A smooth modulus makes the **discrete log** feasible via **Pohlig-Hellman** (we solve the log modulo each small factor of `p-1`, then CRT). This is the intended “clean” attack.

But in this challenge, private exhibitors are drawn into `[1, 100000]`: **small**. So, as for [[Merkle]], a simple **brute force** of the discrete log is enough: `g^i mod p == A` for increasing `i` (`a = 69244`). Then secret `key = B^a mod p`, and `flag = ct XOR key_bytes`.

Flag: `sigpwny{3v3ry0n3_f0rg3t5_4b0u7_m3rkl3_wh3n_d01ng_k3y_3xch4ng3}`.

## Solve script
Script path: `scripts/solve.py`

## Flag
sigpwny{3v3ry0n3_f0rg3t5_4b0u7_m3rkl3_wh3n_d01ng_k3y_3xch4ng3}

## Lessons and reusable patterns
- First smooth (p-1 friable) = DH/ElGamal breakable by Pohlig-Hellman even without exponent
- Here double weakness: bounded exponents -> the direct brute (like Merkle) short-circuits everything.
- Reflex: after a discrete log, the secret often serves as an XOR key (or AES key) on the flag.
- Script: work/solve.py.
