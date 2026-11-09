---
title: "Make-a-Difference"
ctf: "Pwny-CTF"
category: "forensics"
difficulty: "Not specified"
points: 100
techniques: ["forensics"]
tools: ["python"]
keywords: ["Make-a-Difference", "Pwny-CTF", "forensics"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Forensics/Make-a-Difference/notes.md"
---

# Make-a-Difference (Pwny-CTF, forensics)

## Summary
Challenge **Make-a-Difference** from the Pwny-CTF CTF, forensics category. Reflex “two almost identical files”: the difference is the message. cmp -l lists each different byte in the form position value_file1 value_file2, the values ​​being in octal (special feature of cmp).

## Statement and artefacts
Oh jeez both of these files look the same! Hmmm... something does look a bit off though. What's the difference?

Flag format: `flag{..}`

**Author**: Jesse

**Provided files / artifacts:**
- `file1.txt (text, 99.0 KB)`
- `file2.txt (text, 99.0 KB)`

## Recognition signals
- Signal: octal2text translates a list of octal numbers into ASCII characters. Alternative if the tool is missing: printf or a little Python ''.join(chr(int(o,8)) for o in.).
- Signal: Trap: be careful to note that cmp gives octal, not decimal — otherwise the conversion results in gibberish.

## Resolution method
1. Compare the two files and list the different bytes — `cmp -l file1.txt file2.txt | awk '{print $3}'` → outputs the value (in **octal**) of each byte modified in the 2nd file.
2. Convert this sequence of octal codes into readable text — `octal2text` → gives the flag.

## Flag
flag{python_makes_this_way_too_easy}

## Lessons and reusable patterns
- Reflex “two almost identical files”: the difference is the message. cmp -l lists each different byte in the form position value_file1 value_file2, the values ​​being in octal (special feature of cmp).
- awk '{print $3}' = we keep the 3rd column, i.e. the byte of the 2nd file. ($1 = position, $2 = byte of the 1st file.)
- octal2text translates a list of octal numbers into ASCII characters. Alternative if the tool is missing: printf or a little Python ''.join(chr(int(o,8)) for o in...).
- Trap: be careful to note that cmp gives octal, not decimal — otherwise the conversion results in gibberish.
