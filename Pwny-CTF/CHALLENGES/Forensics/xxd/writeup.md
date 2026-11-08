---
title: "xxd"
ctf: "Pwny-CTF"
category: "forensics"
difficulty: "Not specified"
points: 20
techniques: []
tools: ["xxd"]
keywords: ["xxd", "Pwny-CTF", "forensics"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Forensics/xxd/notes.md"
---

# xxd (Pwny-CTF, forensics)

## Summary
Challenge **xxd** from the Pwny-CTF CTF, forensics category. ⚠️ Always read the format of the flag in desc.txt before submitting / over-analyzing: here the drawing just gives F, and the flag is flag{F} (not F, not sigpwny{F}).

## Statement and artefacts
Wow! You look super excited to use this tool. I've only ever seen XD before...

Anyways, the flag is hidden somewhere inside this binary blob... Good luck!

You should solve this challenge using only command-line tools.

Flag format: `flag{...}`

**Author**: Jesse

**Provided files / artifacts:**
- `blob.bin (binary/data, 2.5 KB)`

## Recognition signals
- Signal: Trap that I imposed on myself: do not over-interpret (transposition, autocorrelation, other widths) when the drawing is already readable at width 16.

## Resolution method
1. `xxd blob.bin` → locate the phrase “The flag is:” then a dense zone of characters `P` (0x50) against a background of `.` (0x2e).
2. Display the area at **width 16** (that of `xxd`): `P` read **vertically** draw a letter → here a **`F`**.
   - (fast) `xxd blob.bin | tail -30` is enough to see the `F` form in the ASCII column.
3. Apply the **flag format** given in the description: `Flag format: flag{...}` → **`flag{F}`**.

## Flag
flag{F}

## Lessons and reusable patterns
- ⚠️ Always read the format of the flag in desc.txt before submitting / over-analyzing: here the drawing just gives F, and the flag is flag{F} (not F, not sigpwny{F}).
- A P = 0x50 (printable) on a background of. = 0x2e: perfect for drawing visible letters in a xxd.
- Trap that I imposed on myself: do not over-interpret (transposition, autocorrelation, other widths) when the drawing is already readable at width 16.
