---
title: "the-library-5"
ctf: "Pwny-CTF"
category: "misc"
difficulty: "Not specified"
points: 50
techniques: []
tools: ["strings"]
keywords: ["the-library-5", "Pwny-CTF", "misc", "strings", "elf"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Shell/the-library-5/notes.md"
---

# the-library-5 (Pwny-CTF, misc)

## Summary
Challenge **the-library-5** from the Pwny-CTF CTF, misc category. Strings <binary> lists readable character sequences -> reflex for a flag hidden in an executable.

## Statement and artefacts
The library has an executable in it, can you find the executable and then find the flag in the executable?!

## Recognition signals
Not specified.

## Resolution method
1. Statement: *“find the executable and then find the flag in the executable”*.
2. Locate the executable (ELF): `find findme/ -type f -exec sh -c 'file "$1"|grep -q ELF && echo "$1"' _ {} \;` → `findme/9/1/8/5/ghToM`.
3. Extract the flag: `strings findme/9/1/8/5/ghToM | grep sigpwny` → `sigpwny{string_string_thats_the_thing}` (verified: identical to flag.txt).

## Flag
sigpwny{string_string_thats_the_thing}

## Lessons and reusable patterns
- strings <binary> lists readable character sequences -> reflex for a flag hidden in an executable.
- Locate an executable in a tree: file + ELF filter.
