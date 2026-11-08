---
title: "Just-Another-Logo"
ctf: "Pwny-CTF"
category: "forensics"
difficulty: "Not specified"
points: 20
techniques: ["encoding"]
tools: ["strings"]
keywords: ["Just-Another-Logo", "Pwny-CTF", "forensics", "encoding", "strings"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Forensics/Just-Another-Logo/notes.md"
---

# Just-Another-Logo (Pwny-CTF, forensics)

## Summary
Challenge **Just-Another-Logo** from the Pwny-CTF CTF, forensics category. Main technique: encoding. Basic forensics reflex: on any file (image, binary, etc.), always run strings first. Many “easy” flags are just written in plain text in the bytes of the file.

## Statement and artefacts
Sometimes there are just extra stuff in an image that you gotta see.

Flag format: `flag{...}`

**Author**: Jesse

**Provided files / artifacts:**
- `sigpwny_isnt_the_only_text_in_this_logo.png (image, 3.8 MB)`

## Recognition signals
- Signal: strings only displays by default sequences of at least 4 printable characters. If nothing comes out, try strings -n 3 (shorter threshold) or strings -e l (wide encoding, useful for UTF-16 text on Windows).
- If we observe Trap: the output can be long, consider filtering with strings <file> | grep -i flag.

## Resolution method
1. Search for readable text strings in the image file — `strings <file>` → the flag appears directly in the output.

## Flag
flag{you_cant_hide_from_me_if_you_are_in_plainsight}

## Lessons and reusable patterns
- Basic forensics reflex: on any file (image, binary, etc.), always run strings first. Many “easy” flags are just written in plain text in the bytes of the file.
- strings only displays by default sequences of at least 4 printable characters. If nothing comes out, try strings -n 3 (shorter threshold) or strings -e l (wide encoding, useful for UTF-16 text on Windows).
- Trap: output can be long -> filter with strings <file> | grep -i flag.
