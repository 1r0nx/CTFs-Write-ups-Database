---
title: "Haybales"
ctf: "Pwny-CTF"
category: "misc"
difficulty: "easy"
points: 150
techniques: ["xor-cipher"]
tools: ["python"]
keywords: ["Haybales", "Pwny-CTF", "misc", "xor-cipher", "python", "zip", "xor", "oracle"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Misc/Haybales/notes.md"
---

# Haybales (Pwny-CTF, misc)

## Summary
Challenge **Haybales** from the Pwny-CTF CTF, misc category. Main technique: xor-cipher. 2 flags (in deere_chal.py, method decode_flag):

## Statement and artefacts
Can you reverse the hidden flag in the Deere Game?

**Provided files / artifacts:**
- `work/code.tar.gz (archive, 12.8 KB)`
- `work/work.tar (archive, 63.0 KB)`

## Recognition signals
- If we look at Oracle's decryption = disambiguator, think about when multiple keys pass it.

## Resolution method
1. **The idea**

A MicroPython game for a badge (SSD1306 screen). The flag is only displayed if the variable `self.keys` (history of the last 32 up/down presses, 1 bit each) takes a precise value. `decode_flag()` contains both paths.

2. **Break pio_mix**

The PIO program (`simple_pio`) processes 8 times 4 bits of the OSR (`out(x,1)` + `out(y,3)`) and pushes 4 bits into the ISR (`in(y,3)` + `in(x,1)`). By iteration:
- `jmp(not_x,"skip")`: if x==0, skip the decrement;
- `jmp(y_dec,"skip")` (x==1): **always decrement Y** (if Y==0, Y becomes `0xFFFFFFFF`, no saturation — trap!);
- `mov(y, invert(y))` then `in(y,3)` → pushes `(~y)&7`; `in(x,1)` → push x.

We **brute force the 2^32 values** in C (PIO emulation, ~50 s on 8 cores), testing both shift directions (OUT/IN) because MicroPython allows both. Then we **decrypt each candidate** via SHA-256 ⊕ `encoded`: only the real `key` gives readable text → `key = 0x8661eb95` (shift-left for OUT and IN = MicroPython default).

## Solve script
Script path: `scripts/badgeio.py`
Script path: `scripts/battle_state.py`
Script path: `scripts/deere_chal.py`
Script path: `scripts/menu.py`
Script path: `scripts/pwnymon.py`
Script path: `scripts/sao.py`
Script path: `scripts/sao_util.py`
Script path: `scripts/solve.py`
Script path: `scripts/ssd1306.py`
Script path: `scripts/stats.py`
Script path: `scripts/utils.py`
Script path: `scripts/welcome.py`

## Flag
sigpwny{m1cr0py7h0n_1s_c0ol}

## Lessons and reusable patterns
- Flag conditioned by an internal state (here the press history): read the
- Emulate an RP2040 PIO: 1 instruction = 1 micro-op; pay attention to semantics
- Decryption oracle = disambiguator: when several keys pass the
- XOR + constant table = reflex for any “flag” hidden in code.
