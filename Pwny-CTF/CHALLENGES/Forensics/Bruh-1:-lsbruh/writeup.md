---
title: "Bruh-1:-lsbruh"
ctf: "Pwny-CTF"
category: "forensics"
difficulty: "Not specified"
points: 100
techniques: ["lsb-steganography", "image-steganography"]
tools: ["zsteg"]
keywords: ["Bruh-1:-lsbruh", "Pwny-CTF", "forensics", "lsb-steganography", "image-steganography", "zsteg", "png", "jpg"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Forensics/Bruh-1:-lsbruh/notes.md"
---

# Bruh-1:-lsbruh (Pwny-CTF, forensics)

## Summary
Challenge **Bruh-1:-lsbruh** from the Pwny-CTF CTF, forensics category. Main technique: lsb-steganography. LSB = bits are hidden in the least significant bit of each pixel (invisible to the eye). zsteg (PNG/BMP) tests all plans automatically.

## Statement and artefacts
Use an LSB viewer to find the flag!

Author: Thomas

**Provided files / artifacts:**
- `bruh.jpg.gif.bmp.png (image, 489.3 KB)`

## Recognition signals
- Signal: Distrust: a flag in the metadata can be a decoy when the statement talks about LSB.

## Resolution method
1. `zsteg bruh.jpg.gif.bmp.png` → in the `b1, rgb, lsb, xy` plane: `sigpwny{when_the_lsb_is_sus}` (repeated).
2. ⚠️ The `Comment` field contains a **decoy** (`sigpwny{you_found_the_exif_data!}`) → the real flag is in the LSB.

## Flag
sigpwny{when_the_lsb_is_sus}

## Lessons and reusable patterns
- LSB = bits are hidden in the least significant bit of each pixel (invisible to the eye). zsteg (PNG/BMP) tests all plans automatically.
- Distrust: a flag in the metadata can be a decoy when the statement talks about LSB.
