---
title: "Bruh-0:-Exif"
ctf: "Pwny-CTF"
category: "forensics"
difficulty: "Not specified"
points: 50
techniques: ["exif-metadata"]
tools: ["strings"]
keywords: ["Bruh-0:-Exif", "Pwny-CTF", "forensics", "exif-metadata", "strings", "png", "jpg", "exif"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Forensics/Bruh-0:-Exif/notes.md"
---

# Bruh-0:-Exif (Pwny-CTF, forensics)

## Summary
Challenge **Bruh-0:-Exif** from the Pwny-CTF CTF, forensics category. Main technique: exif-metadata. Basic reflex: strings <img> | grep -i sigpwny first of all.

## Statement and artefacts
The flag is somewhere in the image data in plaintext...

**Provided files / artifacts:**
- `bruh.jpg.gif.bmp.png (image, 489.3 KB)`

## Recognition signals
Not specified.

## Resolution method
1. `strings bruh.jpg.gif.bmp.png | grep sigpwny` → `sigpwny{you_found_the_exif_data!}`.
2. (The file is actually a **PNG** despite its name; the flag is in a text/Comment field.)

## Flag
sigpwny{you_found_the_exif_data!}

## Lessons and reusable patterns
- Basic reflex: strings <img> | grep -i sigpwny first of all.
- Do not trust the extension: file reveals the real type (here PNG).
