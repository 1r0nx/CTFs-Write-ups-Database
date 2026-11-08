---
title: "A-Very-Special-Character-2"
ctf: "Pwny-CTF"
category: "misc"
difficulty: "Not specified"
points: 30
techniques: []
tools: ["netcat"]
keywords: ["A-Very-Special-Character-2", "Pwny-CTF", "misc", "netcat"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Shell/A-Very-Special-Character-2/notes.md"
---

# A-Very-Special-Character-2 (Pwny-CTF, misc)

## Summary
Challenge **A-Very-Special-Character-2** from the Pwny-CTF CTF, misc category. | (pipe) connects the output of one command to the input of another.

## Statement and artefacts
Here's another challenge that needs you to netcat to a server!

`nc chal.sigpwny.com 5003`

This chal is trickier and not something we covered in the meeting. For this chal, you can't type the character it wants you to, so you must pipe the character in from `echo`. `echo` is a linux command. For example, `echo "hello world!" | nc chal.sigpwny.com 5003` will send `hello world!` to the netcat. Instead of hello world, we want to send the ascii value \x07.

## Recognition signals
Not specified.

## Resolution method
1. `nc chal.sigpwny.com 5003` wants a control character (here `\x07`, BEL) that is impossible to type on the keyboard.
2. Generate it with `echo` and pipe it: `echo -e '\x07' | nc chal.sigpwny.com 5003` (or `printf '\x07' | nc...`).
3. Flag = `sigpwny{learned_how_to_pipe}`.

## Flag
sigpwny{learned_how_to_pipe}

## Lessons and reusable patterns
- | (pipe) connects the output of one command to the input of another.
- echo -e /printf to produce raw bytes (\x07, \n…).
