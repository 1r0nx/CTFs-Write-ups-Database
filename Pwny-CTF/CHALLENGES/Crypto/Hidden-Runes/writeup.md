---
title: "Hidden-Runes"
ctf: "Pwny-CTF"
category: "crypto"
difficulty: "Not specified"
points: 150
techniques: ["substitution-cipher"]
tools: ["python"]
keywords: ["Hidden-Runes", "Pwny-CTF", "crypto", "substitution-cipher", "python"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Crypto/Hidden-Runes/notes.md"
---

# Hidden-Runes (Pwny-CTF, crypto)

## Summary
Challenge **Hidden-Runes** from the Pwny-CTF CTF, crypto category. Main technique: substitution-cipher. Weird symbols, ~26 distinct, "broken" but structured text -> mono-alphabetic substitution. The sigpwny{ flag format is a crib that unlocks 7 letters for free.

## Statement and artefacts
A capsule concealing a mysterious message has been discovered on the Main Quad. You heard that those who decipher the message get to be featured in the Daily Illini!

**author**: Sophia

**Provided files / artifacts:**
- `mysterious_message.txt (text, 768 B)`

## Recognition signals
Not specified.

## Resolution method
1. `mysterious_message.txt`: text in astrological symbols (32 distinct glyphs = 26 letters + space/punctuation). Clues: random character substitution, guess by context.
2. **Crib of the flag**: the last line necessarily has the form `sigpwny{...}` → 7 free letters (`♅=s ♇=i ♈=g ♊=p ♏=w ♃=n ♂=y`).
3. **Context analysis** (recognizable words) for the rest:
   - `☉☾♄♄☿!` = “hello!” → h, e, l, l, o
   - `♀♂ ♃♆♀☾ ♇♅` = "my name is" → m, a
   - `♆♄♊☉♆♍☾♎♅` = “alphabets” → l, h, b, t
   - `♅♊♆♋☾` = "space" → c
   - `… ♆♐☾ ♀♆♐♅, ♅♆♎♒♐♃, ♆♃♌ ♊♄♒♎☿.` = "are mars, saturn, and pluto" → r, u, d, o
   - `☽☾♐♂` = "very" → v; `♑♒♃` = “fun” → f
4. Build the `mapping` symbol→letter incrementally, apply with `str.translate` (or `mapping.get(ch, ch)` in a loop to keep unknowns visible), read the flag.

## Discarded approaches
- Tools: quipqiup.com (mono-alphabetic substitution auto solver) · dcode.fr “Monoalphabetic Substitution”.

## Solve script
Script path: `scripts/solve.py`

## Flag
sigpwny{alphabets_and_space_and_mars_are_very_fun}

## Lessons and reusable patterns
- Weird symbols, ~26 distinct, "broken" but structured text -> mono-alphabetic substitution. The sigpwny{ flag format is a crib that unlocks 7 letters for free.
- Always check the bijection (1 symbol ↔ 1 letter): two symbols giving the same letter = false hypothesis.
- Harder variant: without crib, do frequency analysis + patterns (doubled letters, words of 1-2 letters a/i, the, and), or tools (quipqiup).
