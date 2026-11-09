---
title: "Ancient-Scroll-of-Wisdom"
ctf: "Pwny-CTF"
category: "reverse"
difficulty: "Not specified"
points: 900
techniques: ["xor-cipher", "encoding", "vm-reverse"]
tools: ["python"]
keywords: ["Ancient-Scroll-of-Wisdom", "Pwny-CTF", "reverse", "xor-cipher", "encoding", "vm-reverse", "python", "xor"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Rev/Ancient-Scroll-of-Wisdom/notes.md"
---

# Ancient-Scroll-of-Wisdom (Pwny-CTF, reverse)

## Summary
Challenge **Ancient-Scroll-of-Wisdom** from the Pwny-CTF CTF, reverse category. Main technique: xor-cipher. Flag not necessarily in English/ASCII: here the flag IS Chinese. When the reverse spits out consistent CJK codepoints, this is a sign that you need to read them (Google Translate), not look for ASCII.

## Statement and artefacts
In a whirl of gears and light, you activate the time machine. Landing in the Yellow River Valley, you stumble upon a dusty chamber. There, you found a parchment filled with intricate symbols, an ancient programming language, forgotten by time but alive in your hands. Can you figure out what does it do?

I added additional logic to prevent brute-force. This challenge is now **Cameron**-proof. **Author**: Henry

**Provided files / artifacts:**
- `work/scroll.wy (file, 4.3 KB)`

## Recognition signals
- Signal: Extension.wy + indices (“is the flag even in English?
- Signal: », Google Translate) = wenyan-lang.
- If we look at Interpreter, think of @wenyanlang/core (npm).
- Signal: The 吾嘗觀「「X」」之書。方悟「f」之義。 are imports from standard libraries.

## Resolution method
1. **What the scroll does**

- Imports: `算經` (floor/pow/π/e/abs), `曆法` (`彼年何年號`), `質問` (input), `位經` (XOR).
- `碼(文,位)` = `charCodeAt`. `密(n)` = base-12 with the 12 animals `鼠牛虎兔龍蛇馬羊猴雞犬豕` as digits (鼠=0).
- Flag length imposed = `floor(π^e)+2 = 24`.
- Constants: `妙文 = 彼年何年號()` → **"西元"** (“CE” era for a modern date, therefore stable, not dated — checked via the interpreter); `戲數="六十九"`; `嬉數="四百二十"` (used as **strings**, we take their `charCodeAt`).
- Validation, for each position `i` from 0 to 23:
  ```
  字 = ( flag.charCodeAt(i)*2 − 妙文[i%2] + 戲數[i%3] ) XOR 嬉數[i%4]
  临 = abs( 字 − 字_previous )           #字_previous = 0 initially
  密文 = 密(临) zero-padded 5-digit-zodiac
  答_reconstructed += 密文
  ```
Must equal the constant `答` (24×5 = 120 zodiac characters).

2. **Reverse**

1. Decode `答` → 24 `临` values (blocks of 5 base-12 digits).
2. GB up: `字ᵢ = 字ᵢ₋₁ ± 临ᵢ` (ambiguity of `abs`), then `charCode = ( (字 XOR 嬉數[i%4]) + 妙文[i%2] − 戲數[i%3] ) / 2`.
3. Prune the sign tree by **parity** (integer charCode → `val` even) **+ “text” codepoint** (ASCII/CJK/CJK punctuation). Remaining 12 candidates; **only one** is a well-formed sentence `西格普尼「…。」`.
4. Emulate the `XOR` **a la JS (signed Int32)**, otherwise the negative values diverge.

Verification: re-encoding the flag found should return `答` (self-check), and the interpreter responds `此旗然矣。`.

See `work/solve.py` (autonomous reverse + re-encoding verification). Install the interpreter to re-check: `npm i @wenyanlang/core`.

3. **Recognize**

Extension `.wy` + indices (“is the flag even in English?”, Google Translate) = **wenyan-lang**. Interpreter: `@wenyanlang/core` (npm). `吾嘗觀「「X」」之書。方悟「f」之義。` are standard library imports.

## Solve script
Script path: [scripts/solve.py](scripts/solve.py)

## Flag
西格普尼「西格普尼，伊利諾州之州學之資安社也。」

## Lessons and reusable patterns
- Flag not necessarily in English/ASCII: here the flag IS Chinese. When the reverse spits out consistent CJK codepoints, this is a sign that you need to read them (Google Translate), not look for ASCII.
- abs = loss of information: a string 临ᵢ = abs(字ᵢ − 字ᵢ₋₁) couples each character to the previous one -> impossible to brute-force independently (this is the “anti-brute-force / Cameron-proof” of the challenge). The ambiguity is removed by an external constraint (readable text).
- Faithfully emulate the target language operators: wenyan's 異或 = signed 32-bit XOR JS.
- Determine questionable constants by executing rather than guessing: 彼年何年號() returns "西元", confirmed by running the interpreter on a mini-program.
