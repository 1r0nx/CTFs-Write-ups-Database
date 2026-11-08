---
title: "the-library-4"
ctf: "Pwny-CTF"
category: "misc"
difficulty: "Not specified"
points: 50
techniques: []
tools: ["strings"]
keywords: ["the-library-4", "Pwny-CTF", "misc", "strings", "png"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Shell/the-library-4/notes.md"
---

# the-library-4 (Pwny-CTF, misc)

## Summary
Challenge **the-library-4** from the Pwny-CTF CTF, misc category. Grep/strings are not enough for a flag drawn in an image -> you have to look at it.

## Statement and artefacts
There is one image in the folder, maybe it has a flag in it. It might be a png...

## Recognition signals
Not specified.

## Resolution method
1. Statement: *“one image in the folder, maybe it has a flag in it. It might be a png..."*.
2. Find the image: `find findme/ -iname '*.png'` → `findme/3/0/8/9/aklUbG.png`.
3. Open the image (viewer / `xdg-open`, or here direct reading) → the flag is **written by hand**: `sigpwny{MS_Paint_lol_Pog}` (verified: identical to flag.txt).

## Flag
sigpwny{MS_Paint_lol_Pog}

## Lessons and reusable patterns
- grep/strings are not enough for a flag drawn in an image -> you have to look at it.
- find -iname '*.png' to locate an image in a tree.
