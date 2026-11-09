---
title: "Flag-Vault"
ctf: "Pwny-CTF"
category: "pwn"
difficulty: "Not specified"
points: 150
techniques: ["password-cracking"]
tools: ["netcat", "python"]
keywords: ["Flag-Vault", "Pwny-CTF", "pwn", "netcat", "python"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Pwn/Flag-Vault/notes.md"
---

# Flag-Vault (Pwny-CTF, pwn)

## Summary
Challenge **Flag-Vault** from the Pwny-CTF CTF, pwn category. Temporal side-channel: when the processing time depends on the secret (comparison not at constant time, early-exit), it leaks the secret. Here each correct digit = +10 M iterations ≈ +0.7-1 s, largely measurable even via the network.

## Statement and artefacts
Since Fall CTF flags are so sensitive, we want to make absolutely sure flag vault users have the correct PIN before accessing it. Can you bypass our protections, or maybe even use them against us, and figure out the PIN?

Connect with `nc chal.sigpwny.com 6002`.

Note: The PIN consists of 9 digits, each a number 0 through 9 (e.g. 1234567890). To run `chal.py` locally, create pin.txt and flag.txt files with your own values ​​for testing.

**author**: kmh

**Provided files / artifacts:**

## Recognition signals
- Signal: A correct digit rotates the loop for 10 M iterations (slow) before moving on to the next one; a false digit comes out immediately (fast).
- Signal: So response time ∝ number of correct digits at the top.
- Signal: Temporal side-channel: when the processing time depends on the secret (comparison not at constant time, early-exit), it leaks the secret. Here each correct digit = +10 M iterations ≈ +0.7-1 s, largely measurable even via the network.
- Signal: Late positions are slower to measure (the correct prefixes accumulate): this is normal, the signal remains = +1 loop for the correct digit.

## Resolution method
1. The free clue directs: “Checking something ten million times... Can the program's execution time leak information? ".
2. PIN = 9 digits. Left→right reconstruction: at each position, with the prefix already found, test the 10 digits (rest filled with `0`, length 9) and measure the time.
3. The correct number is the one whose response is **slowest** (it went through a loop 10M more). Averaging 2 measurements smoothes the network jitter.
4. Full PIN → the server displays the flag.

PIN found: `493928507`.

See `work/solve.py`. Unrolled: for each position, `measure(prefix + digit + "0"*remainder)` ×10, keep the max; then reconnect with the full PIN to read `sigpwny{...}`.

1. **Flaw (chal.py)**

```python
for i in range(len(user_pin)):
    for _ in range(10000000):            #10 M times per digit
        if user_pin[i] != correct_pin[i]:
            print('Incorrect PIN.'); raise SystemExit(0)
```
A **correct** digit runs the loop for 10 M iterations (slow) before moving on to the next one; a **false** digit comes out immediately (fast). So **response time ∝ number of correct digits at the top**.

## Solve script
Script path: [scripts/solve.py](scripts/solve.py)

## Flag
sigpwny{b4d_t1ming_:(}

## Lessons and reusable patterns
- Temporal side-channel: when the processing time depends on the secret (non-constant time comparison, early-exit), it leaks the secret. Here each correct digit = +10 M iterations ≈ +0.7-1 s, largely measurable even via the network.
- Constant time comparison = the parade (compare all characters whatever happens, without anticipated return/exit). Early-exit is the classic anti-pattern (see == on passwords/HMAC).
- Linear attack (10 digits × 9 positions), not exponential: we never brute-force the 10⁹ PIN, we reconstruct digit by digit using the channel.
- Late positions are slower to measure (the correct prefixes accumulate): this is normal, the signal remains = +1 loop for the correct digit.
