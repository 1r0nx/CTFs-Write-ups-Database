---
title: "Format-String-Quiz"
ctf: "Pwny-CTF"
category: "pwn"
difficulty: "Not specified"
points: 100
techniques: ["format-string", "nx-bypass", "encoding"]
tools: ["netcat"]
keywords: ["Format-String-Quiz", "Pwny-CTF", "pwn", "format-string", "nx-bypass", "encoding", "netcat", "hex", "padding"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/PWN-II/Format-String-Quiz/notes.md"
---

# Format-String-Quiz (Pwny-CTF, pwn)

## Summary
Challenge **Format-String-Quiz** from the Pwny-CTF CTF, pwn category. Main technique: format-string. %N$x = position (which argument to read); %Nx = width (how many characters to display, padded with spaces). Never mix the two syntaxes.

## Statement and artefacts
Can you answer all the questions correctly?

`nc chal.sigpwny.com 1373`

**Author**: Nathan

**Provided files / artifacts:**

## Recognition signals
Not specified.

## Resolution method
1. `nc chal.sigpwny.com 1373` — no binary or source, a pure knowledge quiz on `printf`, with unlimited retry in case of wrong answer.
2. Base specifiers: `%s` (string), `%x` (hex integer, **4 bytes**), `%p` (pointer, **8 bytes on a 64-bit system** — same family as `%x` but different size).
3. Positional syntax: `%N$specifier` directly reads the Nth argument (e.g. `%15$s` = the string pointed to by the 15th argument), without having to consume the previous 14 with `%p` in the chain.
4. Pitfall of question 5: “int hex completed with spaces to make 100 characters in total” is **not** a matter of position — it is a **width of field**: `%100x` (without `$`). `%100$x` would have read the 100th argument, which has nothing to do with padding.

## Flag
sigpwny{aced_the_format_string_quiz}

## Lessons and reusable patterns
- %N$x = position (which argument to read); %Nx = width (how many characters to display, padded with spaces). Never mix the two syntaxes.
- Sizes to remember: %x/%d = 4 bytes (int), %p/%lx = 8 bytes over 64 bits (pointer/long) — important for aligning a offset_browser or a fmtstr_payload with real challenges (Format 0, 4 - Format, Bug Bounty 6).
- Purely theoretical, but these are exactly the bases used to calculate the offset of a real format string exploit.
