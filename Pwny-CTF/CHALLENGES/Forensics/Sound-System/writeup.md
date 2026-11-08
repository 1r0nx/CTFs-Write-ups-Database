---
title: "Sound-System"
ctf: "Pwny-CTF"
category: "forensics"
difficulty: "Not specified"
points: 100
techniques: []
tools: ["steghide"]
keywords: ["Sound-System", "Pwny-CTF", "forensics", "steghide", "jpg"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Forensics/Sound-System/notes.md"
---

# Sound-System (Pwny-CTF, forensics)

## Summary
Challenge **Sound-System** from the Pwny-CTF CTF, forensics category. A “repetitive green noise” image = often a stereogram (Magic Eye). Clue here: “stereo system”.

## Statement and artefacts
Hey look at this weird image. My friend said that it encrypted it with a stereo system.

Wrap the message you find in `sigpwny{}`

**Provided files / artifacts:**
- `steg100_9075898.jpg (image, 670.2 KB)`

## Recognition signals
- Signal: A “repetitive green noise” image = often a stereogram (Magic Eye). Clue here: “stereo system”.

## Resolution method
1. The image `steg100_9075898.jpg` looks like repetitive noise → it is an **autostereogram**.
2. Reveal the 3D pattern: squint (cross/parallel vision) **or** use a stereogram decoder (e.g. online tools/offset autocorrelation scripts).
3. The hidden word appears → wrap it: `sigpwny{Psyloflag}`.

## Flag
sigpwny{Psyloflag}

## Lessons and reusable patterns
- A “repetitive green noise” image often = a stereogram (Magic Eye). Clue here: “stereo system”.
- Not metadata / LSB / steghide: it's visual (depth perception).
