---
title: "Image"
ctf: "Pwny-CTF"
category: "forensics"
difficulty: "Not specified"
points: 25
techniques: ["format-string"]
tools: ["xxd", "tar"]
keywords: ["Image", "Pwny-CTF", "forensics", "format-string", "xxd", "tar", "png"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Forensics/Image/notes.md"
---

# Image (Pwny-CTF, forensics)

## Summary
Challenge **Image** from the Pwny-CTF CTF, forensics category. Main technique: format-string. Format string:.png (false) -> gzip -> tar -> flag. Always file + xxd | head to check.

## Statement and artefacts
...or is it?

**Provided files / artifacts:**
- `flag.png (image, 148 B)`
- `flag.tar (archive, 10.0 KB)`

## Recognition signals
Not specified.

## Resolution method
1. `file flag.png` → it's **not** a PNG but a **gzip**! ("...or is it?")
2. Uncompress: `zcat flag.png > flag.tar` → a **tar archive**.
3. Extract: `tar -xOf flag.tar` → `sigpwny{compressed_fossil}`.

## Flag
sigpwny{compressed_fossil}

## Lessons and reusable patterns
- Format string:.png (false) -> gzip -> tar -> flag. Always file + xxd | head to check.
- “fossil” = the disguised format.
