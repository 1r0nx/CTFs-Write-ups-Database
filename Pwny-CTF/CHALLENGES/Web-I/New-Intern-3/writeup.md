---
title: "New-Intern-3"
ctf: "Pwny-CTF"
category: "web"
difficulty: "Not specified"
points: 200
techniques: []
tools: []
keywords: ["New-Intern-3", "Pwny-CTF", "web", "http"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Web-I/New-Intern-3/notes.md"
---

# New-Intern-3 (Pwny-CTF, web)

## Summary
Challenge **New-Intern-3** from the Pwny-CTF CTF, web category. Logical continuation of “New Intern 1/2”: verification/secret is on the client side. Web Reflexes I: read HTML (Ctrl+U / Inspector), JS files, comments, and look at “forgotten” files (/robots.txt,.js,.bak).

## Statement and artefacts
OSU also fired me. This time I made sure my new employer, Michigan, could never get hacked!

Can you find the passcode and login?

http://new-intern-3.chal.sigpwny.com

**author**: Pete

**Provided files / artifacts:**
- `info.txt (text, 19 B)`

## Recognition signals
Not specified.

## Resolution method
1. Recovery of the connection password: `5up3r_SecUr3_pass?!` (noted in `info.txt`).
2. Connection with this password → flag `sigpwny{why_didnt_i_get_a_return_offer}`.

1. > ⚠️ Exact password discovery method **to be confirmed** (probably in the page source code, an HTML comment, a JS file or a hidden endpoint). To be completed when we revisit the challenge together.

## Flag
sigpwny{why_didnt_i_get_a_return_offer}

## Lessons and reusable patterns
- Logical continuation of “New Intern 1/2”: verification / secrecy is on the client side. Web Reflexes I: read HTML (Ctrl+U / Inspector), JS files, comments, and look at “forgotten” files (/robots.txt,.js,.bak).
- Recognize this type: “login” challenge without apparent server logic -> the secret is hidden somewhere in what the browser downloads.
