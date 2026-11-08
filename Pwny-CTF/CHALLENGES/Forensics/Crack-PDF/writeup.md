---
title: "Crack-PDF"
ctf: "Pwny-CTF"
category: "forensics"
difficulty: "Not specified"
points: 150
techniques: ["password-cracking", "hash-cracking"]
tools: ["john", "hashcat"]
keywords: ["Crack-PDF", "Pwny-CTF", "forensics", "password-cracking", "hash-cracking", "john", "hashcat"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Forensics/Crack-PDF/notes.md"
---

# Crack-PDF (Pwny-CTF, forensics)

## Summary
Challenge **Crack-PDF** from the Pwny-CTF CTF, forensics category. Main technique: password-cracking. Encrypted PDF -> pdf2john (in the John suite) to output the hash, then john/hashcat (mode 10500/10700 depending on the PDF version) with rockyou.

## Statement and artefacts
(Based on a true story)

I bought a PDF textbook for a class, but it was encrypted. I forgot the password to the PDF. Could you help me crack it?

The original owner of the PDF claims that the password was "something like `abc123` or `123abc`" --- but we're not so sure. Human memory can be unreliable.

Can you find the password?

**Author**: Husnain

**Provided files / artifacts:**
- `dec.pdf (document, 256.5 KB)`
- `encrypted.pdf (document, 258.5 KB)`
- `hash (file, 207 B)`
- `pdf.pot (file, 200 B)`

## Recognition signals
- If we observe ⚠️ Format trap, thinking about this challenge expects the raw flag (abcdef), not sigpwny{abcdef}.
- Signal: Lesson: if an “obvious” flag returns a Regex parse error, try the bare value (without the sigpwny{} wrapper) — the author stored a regex flag without a wrapper.

## Resolution method
1. Extract hash from PDF — `pdf2john encrypted.pdf > hash` (`$pdf$...` format).
2. Cracker — `john hash --wordlist=rockyou.txt` → password **`abcdef`** (consistent with the clue “something like `abc123` or `123abc`”).
3. (optional) Decrypt PDF: `qpdf --password=abcdef --decrypt encrypted.pdf dec.pdf`.
4. The flag is the password itself: **`abcdef`**.

## Flag
abcdef

## Lessons and reusable patterns
- Encrypted PDF -> pdf2john (in the John suite) to output the hash, then john/hashcat (mode 10500/10700 depending on the PDF version) with rockyou.
- ⚠️ Format trap: this challenge expects the raw flag (abcdef), not sigpwny{abcdef}.
- The flag is of type regex on the CTFd side. Submitting sigpwny{abcdef} triggers "Regex parse error occured" because curly braces { } are regex metacharacters.
- Lesson: if an “obvious” flag returns a Regex parse error, try the bare value (without the sigpwny{} wrapper) — the author stored a regex flag without a wrapper.
- The statement said: “Can you find the password? » -> the flag IS the password.
