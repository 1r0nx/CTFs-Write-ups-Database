---
title: "Dead-Air"
ctf: "2026-hiCTF"
category: "misc"
difficulty: "Not specified"
points: null
techniques: ["vigenere", "substitution-cipher", "audio-steganography", "encoding"]
tools: ["7z"]
keywords: ["Dead-Air", "hiCTF", "misc", "vigenere", "substitution-cipher", "audio-steganography", "encoding", "7z", "png"]
status: "solved"
has_script: false
source: "hiCTF/misc/Dead-Air/notes.md"
---

# Dead-Air (hiCTF, misc)

## Summary
Challenge **Dead-Air** from the hiCTF CTF, misc category. Main technique: vigenere. KESTREL numbers station gone silent. “One spoke out loud. The other never made a sound you could hear.

## Statement and artefacts
KESTREL numbers station gone silent. “One spoke out loud. The other never made a sound you could hear. »

**Provided files / artifacts:**
- `dead-air.zip (archive, 9.0 MB)`

## Recognition signals
- Signal: Case: the codepad is in UPPER CASE, but the hiCTF flag is in lower case leet. (This is what caused the first attempts to fail.).
- Signal: Suffix 6r3v: does not form a word (leet G -> 6 ⇒ “GREV”) but is part of the message — anti-guessing suffix, to be kept as is.
- Signal: Vigenère base-37 (not 26) because the alphabet includes numbers and _; the key also advances on the _ of the cipher.
- Signal: The gray dots are not noise: it is the redundancy that locks the reading.

## Resolution method
1. **Resolution chain**

1. **Stereo WAV — two channels to be processed separately**:
   - **Left channel** (loud, keyed tone 699 Hz) = **Morse** → *“KESTREL STATION OFF AIR — KEY IS NIGHTJAR — LISTEN WITH YOUR EYES”*. Gives the **key** (NIGHTJAR) and the instruction (look at a spectrogram).
   - **Right channel** (inaudible, carrier ~13 kHz): its **spectrogram** displays `KSTR-7742-VXQ` = **7z password** (“listen with your eyes”).
2. **7z** (`7z x -pKSTR-7742-VXQ`) → `logbook_page.png` (28 symbols = encrypted) + `operator_codepad.png` (37 symbols = **legend** A-Z, 0-9, `_`).
3. **Symbol decoding via codepad** → encrypted `59R_6L3Q9BYGBQ3QZAYZMP3QIZ92`.
   - **Double redundant encoding**: each cell has a **glyph** AND a **gray dot pattern** (3x4 grid, 3-4 dots). The codepad defines the two captions; both give the **same** encrypted (error-proof cross-check).
4. **Vigenère base-37** (pad alphabet A-Z0-9_), key **NIGHTJAR**, **subtraction**, the key advancing on **each** character: `59R_6L3Q9BYGBQ3QZAYZMP3QIZ92` → `S1L3NC3_W4S_TH3_M3SS4G3_6R3V` = “SILENCE WAS THE MESSAGE” + `6R3V`.
5. **Flag** = the plaintext in **lowercase**: `hiCTF{s1l3nc3_w4s_th3_m3ss4g3_6r3v}`.

2. **Traps**

- **Case**: the codepad is in UPPER CASE, but the hiCTF flag is in **lower case** leet. (This is what caused the first attempts to fail.)
- **Suffix `6r3v`**: does not form a word (leet G→6 ⇒ “GREV”) but is **part** of the message — anti-guessing suffix, to be kept as is.
- Vigenère **base-37** (not 26) because the alphabet includes numbers and `_`; the key also advances on the `_` of the cipher.
- The gray dots are **not** noise: it's the **redundancy** that locks the reading.

## Discarded approaches
- WAV LSB (1-2 bits, L/R) = pure noise; WAV = fmt +data without extra bytes; PNG/7z without hidden data or comments.
- Independently re-decoded Morse code = exactly the text above; right channel = only KSTR-7742-VXQ.

## Flag
hiCTF{s1l3nc3_w4s_th3_m3ss4g3_6r3v}

## Lessons and reusable patterns
- Stereo WAV: analyze each channel separately (one audible = Morse, one “data” = spectrogram).
- Text in a spectrogram (HF/ultrasound carrier) = “to look at” message (STFT -> image).
- Code pad glyph->character = substitution; recognize by related components + IoU; validate by self-recognizing the pad and via redundancy (here the points) if present.
- Vigenère base-N when the alphabet includes digits/_: index each symbol in the alphabet of the pad; test subtraction/addition/Beaufort.
- Flag case: an uppercase alphabet does not imply an uppercase flag — test both (hiCTF = lowercase leet).
