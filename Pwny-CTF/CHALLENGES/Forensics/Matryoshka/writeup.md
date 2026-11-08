---
title: "Matryoshka"
ctf: "Pwny-CTF"
category: "forensics"
difficulty: "Not specified"
points: 200
techniques: ["disk-forensics"]
tools: ["binwalk", "steghide", "zsteg", "7z"]
keywords: ["Matryoshka", "Pwny-CTF", "forensics", "disk-forensics", "binwalk", "steghide", "zsteg", "7z", "png", "jpg"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Forensics/Matryoshka/notes.md"
---

# Matryoshka (Pwny-CTF, forensics)

## Summary
Challenge **Matryoshka** from the Pwny-CTF CTF, forensics category. Main technique: disk-forensics. Multi-layer reflex: file -> extract -> reread the clues -> start again. Keep layers in subfolders so you don't get lost.

## Statement and artefacts
Alright, so I lost a flag somewhere down there. Can you help retrieve it?

Flag format: `flag{...}`

**Author**: Jesse

**Provided files / artifacts:**
- `bcdedit.png (image, 15.9 KB)`
- `deep.7z (archive, 1.6 MB)`
- `frame.png (image, 2.3 KB)`
- `hidden.pdf (document, 42.6 KB)`
- `hnl.jpg (image, 309.4 KB)`
- `in.7z (archive, 1.7 MB)`
- `manoa.jpg (image, 1.3 MB)`
- `now.7z (archive, 1.3 MB)`
- `oahu.jpg (image, 149.8 KB)`
- `unveil.txt (text, 15.5 KB)`
- `we.7z (archive, 1.7 MB)`

## Recognition signals
Not specified.

## Resolution method
1. **Method (principle)**

1. The folder contains a cascade: archives `*.7z` (`in.7z`, `now.7z`, `we.7z`, `deep.7z`), a `hidden.pdf`, images (`hnl.jpg`, `manoa.jpg`, `oahu.jpg`, `frame.png`, `bcdedit.png`) and `unveil.txt`.
2. At each step: identify the type (`file`), extract (`7z x`, `binwalk -e`), read the indices (file names, `unveil.txt`, metadata), and continue on to the next layer (extraction / stegano).
3. Final flag: `flag{i'll_sT1cK_t0_American_d0LLs}` (pun *matryoshka* = American dolls).

## Flag
flag{i'll_sT1cK_t0_American_d0LLs}

## Lessons and reusable patterns
- Multi-layer reflex: file -> extract -> reread the clues -> start again. Keep layers in subfolders so you don't get lost.
- Tools: 7z x, binwalk -e, pdfdetach/pdfimages, zsteg/steghide depending on the layer.
