---
title: "Inside-the-Hackerman"
ctf: "Pwny-CTF"
category: "forensics"
difficulty: "Not specified"
points: 50
techniques: ["disk-forensics"]
tools: ["binwalk", "unzip"]
keywords: ["Inside-the-Hackerman", "Pwny-CTF", "forensics", "disk-forensics", "binwalk", "unzip", "zip", "png"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Forensics/Inside-the-Hackerman/notes.md"
---

# Inside-the-Hackerman (Pwny-CTF, forensics)

## Summary
Challenge **Inside-the-Hackerman** from the Pwny-CTF CTF, forensics category. Main technique: disk-forensics. “Suspicious” image reflex: binwalk to locate files hidden after the header, then binwalk -e/unzip to extract.

## Statement and artefacts
Oh wow thats a really suspicious image. Something has to be hidden in it right?

Flag format: `flag{...}`

**Author**: Jesse

**Provided files / artifacts:**
- `inside_the_hackerman.png (image, 827.4 KB)`

## Recognition signals
Not specified.

## Resolution method
1. `binwalk inside_the_hackerman.png` → a **ZIP** is concatenated after the PNG (offset `0xCE4F4`).
2. Extract: `binwalk -e` (or `unzip`) → `flag.txt`: `flag{good_thing_there_isnt_anything_suspicious_in_this_suspicious_zip_file}`.

## Flag
flag{good_thing_there_isnt_anything_suspicious_in_this_suspicious_zip_file}

## Lessons and reusable patterns
- “Suspicious” image reflex: binwalk to locate files hidden after the header, then binwalk -e/unzip to extract.
