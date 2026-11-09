---
title: "BOF-Demigod"
ctf: "Pwny-CTF"
category: "pwn"
difficulty: "Not specified"
points: 150
techniques: ["buffer-overflow", "stack-canary"]
tools: ["pwntools", "hexdump", "netcat", "python"]
keywords: ["BOF-Demigod", "Pwny-CTF", "pwn", "buffer-overflow", "stack-canary", "pwntools", "hexdump", "netcat", "python", "canary", "stack"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Pwn/BOF-Demigod/notes.md"
---

# BOF-Demigod (Pwny-CTF, pwn)

## Summary
Challenge **BOF-Demigod** from the Pwny-CTF CTF, pwn category. Main technique: buffer-overflow. Defeat randomization by escape: when the layout changes each turn but it is displayed (hexdump, “draw the stack”), we read it instead of guessing it. Same reflex as a real pwn where the program draws the stack: the offsets are calculated, no need for bruteforce.

## Statement and artefacts
Can you solve this Buffer overflow challenge!?! Its different EVERY TIME!

`nc chal.sigpwny.com 3601`

**Provided files / artifacts:**

## Recognition signals
- Signal: To reach CHANGEME (offset before+4) you need len(resp) ≥ before+12; but the overwriting starts from the beginning, so we necessarily go over Beep -> we have to rewrite it exactly.
- Signal: By stopping right at before+12, Borp remains the original (via buf[len(resp):]) and does not have to be rewritten.
- Signal: Defeat randomization by escape: when the layout changes each turn but it is displayed (hexdump, “draw the stack”), we read it instead of guessing it. Same reflex as a real pwn where the program draws the stack: the offsets are calculated, no need for bruteforce.
- Signal: Length trap: len(resp) must be exactly before+12; longer would crush Borp, shorter would not reach CHANGEME.

## Resolution method
1. **Nature of the challenge**

No binary: `server.py` **simulates** an overflow. It shows a hexdump of the buffer, reads a line, then `newbuf = resp + buf[len(resp):]` (your input overwrites the front, the rest keeps its value). 100 winning spins in a row → flag.

Buffer: `[\x00 × before][Beep][CHANGEME][Borp][\x00 × after]`, with `before`/`after` = **16 or 32 drawn at random each round**.

2. **Victory condition**

```
newbuf[before   : before+4]  == "Beep"        # left sentinel: intact
newbuf[before+4 : before+12] != "CHANGEME"    # target: corrupted
newbuf[before+12: before+16] == "Borp"        # right sentinel: intact
```

1. **Understanding the overwrite model** `newbuf = resp + buf[len(resp):]` (overflow from the front).
2. **Parse the hexdump** to reconstruct the bytes → `before` = position of `Beep` (`\x42\x65\x65\x70`). Check: `before ∈ {16, 32}`.
3. **Payload of a turn**: `b"A"*before + b"Beep" + b"A"*8` (length `before+12`). Rewrite `Beep`, put `AAAAAAAA` ≠ `CHANGEME`, leave `Borp`.
4. **Automate 100 rounds** (pwntools): `recvuntil("Input > ")` → parse → `sendline(payload)` → check `Good Job keep going`. After 100 → `sigpwny{...}`.

See `work/solve.py`. Continuation: `recvuntil("Input > ")` → `parse_before()` (position of `Beep` in the reconstructed hexdump) → `sendline(b"A"*before + b"Beep" + b"A"*8)` → ×100 → `sigpwny{...}`.

3. **The trap (the lesson)**

To reach `CHANGEME` (offset `before+4`) you need `len(resp) ≥ before+12`; but the overwriting starts from the **beginning**, so we necessarily pass **over `Beep`** → we are obliged to **rewrite it exactly**. By stopping right at `before+12`, `Borp` remains the original (via `buf[len(resp):]`) and does not have to be rewritten.

## Solve script
Script path: [scripts/server.py](scripts/server.py)
Script path: [scripts/solve.py](scripts/solve.py)

## Flag
sigpwny{n0w_I_c@n_b0f_anyth1ng!}

## Lessons and reusable patterns
- Defeat randomization by escape: when the layout changes each turn but it is displayed (hexdump, “draw the stack”), we read it instead of guessing it. Same reflex as a real pwn where the program draws the stack: the offsets are calculated, no need for bruteforce.
- Preserve the witness bytes: reaching a distant target involves overwriting what is in front -> faithfully reproducing the untouchable values (here Beep; in real life: canary, saved RBP, neighboring pointer). Stopping before the right terminal (Borp) avoids having to rewrite it.
- Recognize: statement “different EVERY TIME” + a dump provided at each iteration = challenge to parse + respond in a loop, scripted.
- Length trap: len(resp) must be exactly before+12; longer would crush Borp, shorter would not reach CHANGEME.
