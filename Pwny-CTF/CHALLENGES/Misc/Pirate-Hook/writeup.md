---
title: "Pirate-Hook"
ctf: "Pwny-CTF"
category: "misc"
difficulty: "Not specified"
points: 550
techniques: ["xor-cipher", "reverse-engineering"]
tools: ["strings", "python"]
keywords: ["Pirate-Hook", "Pwny-CTF", "misc", "xor-cipher", "reverse-engineering", "strings", "python", "xor"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Misc/Pirate-Hook/notes.md"
---

# Pirate-Hook (Pwny-CTF, misc)

## Summary
Challenge **Pirate-Hook** from the Pwny-CTF CTF, misc category. Main technique: xor-cipher. 3rd clone of the same pattern (Immortal-Kitten, Permission-Slip, Pirate-Hook): game

## Statement and artefacts
Ahoy matey! Can you get me treasure back?

**Provided files / artifacts:**
- `work/pirate-hook.exe (binary, 269.5 KB)`

## Recognition signals
- If we observe Read the key as text, think of here the dwords give BOOTY!!! (ASCII) — index.

## Resolution method
1. **The idea**

Windows console game “PIRATE'S HOOK”: navigation function always returns **wrong coordinates**; the hint says to **hook** this function. But, like [[Immortal-Kitten]] / [[Permission-Slip]], the victory flag is **hard-encrypted** by a repeated key XOR → **static** decryption, without hooks or execution.

1. `strings` → pirate theme + `Ye found the treasure chest!`, no clear flag.
2. **Disassemble** and locate the routine (@0x140006230):
   - 8 byte key: dwords `0x544f4f42`, `0x21212159` → `42 4f 4f 54 59 21 21 21` = **`BOOTY!!!`**;
   - ciphertext: 7 dwords @`[rbp-0x28]` **+ 1 WORD** `0x5c29` @`[rbp-0xc]` = **30 bytes**;
   - `flag[i] = ciphertext[i] XOR key[i & 7]`.

## Solve script
Script path: [scripts/solve.py](scripts/solve.py)

## Flag
sigpwny{4rr6h_my_tr34sUr3_m4p}

## Lessons and reusable patterns
- 3rd clone of the same pattern (Immortal-Kitten, Permission-Slip, Pirate-Hook): game
- xor loop …, byte[rbp+rax] with and eax,0x7.
- Read the key as text: here the dwords give BOOTY!!! (ASCII) — index
- Capture the entire length: dwords + residual WORD/BYTE (mov WORD,
