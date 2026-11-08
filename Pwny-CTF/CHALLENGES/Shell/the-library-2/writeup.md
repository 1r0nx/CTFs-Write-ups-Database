---
title: "the-library-2"
ctf: "Pwny-CTF"
category: "misc"
difficulty: "Not specified"
points: 50
techniques: []
tools: []
keywords: ["the-library-2", "Pwny-CTF", "misc"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Shell/the-library-2/notes.md"
---

# the-library-2 (Pwny-CTF, misc)

## Summary
Challenge **the-library-2** from the Pwny-CTF CTF, misc category. Lures: grep -r sigpwny findme returns two false flags in the content (get_a_grep_on_the_situation, string_string_thats_the_thing) to trap anyone looking in the wrong place.

## Statement and artefacts
Now that you have the library, the flag is in one of the file names! GB find it to get some pwnypoints!

## Recognition signals
Not specified.

## Resolution method
1. The statement says: *“the flag is in one of the file **names**”*.
2. Look for the flag in the **names**: `find findme -name "*sigpwny*"` → `.../4/7/2/5/sigpwny{ya_ha_ha_you_found_me}.txt`.
3. Flag = `sigpwny{ya_ha_ha_you_found_me}`.

## Flag
sigpwny{ya_ha_ha_you_found_me}

## Lessons and reusable patterns
- Lures: grep -r sigpwny findme returns two false flags in the content (get_a_grep_on_the_situation, string_string_thats_the_thing) to trap anyone looking in the wrong place.
- find -name "pattern" searches in names; grep -r pattern searches the content. Choose carefully according to the statement.
- grep -a treats binary files as text (useful for seeing binary file matches).
- Reflex: reread the description — it explicitly said “file names”.
