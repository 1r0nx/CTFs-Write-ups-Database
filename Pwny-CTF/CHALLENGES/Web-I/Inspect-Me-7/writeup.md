---
title: "Inspect-Me-7"
ctf: "Pwny-CTF"
category: "web"
difficulty: "Not specified"
points: 50
techniques: ["encoding", "web-exploitation"]
tools: ["curl"]
keywords: ["Inspect-Me-7", "Pwny-CTF", "web", "curl", "http"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Web-I/Inspect-Me-7/notes.md"
---

# Inspect-Me-7 (Pwny-CTF, web)

## Summary
Challenge **Inspect-Me-7** from the Pwny-CTF CTF, web category. “Inspect” a page ≠ HTML only: also check HTTP headers, cookies (Set-Cookie), JS/CSS, comments, robots.txt.

## Statement and artefacts
There are many secret flags lying in [this webpage](http://inspect-me.chal.sigpwny.com/) - can you find them?

Flag format: `flag{...}`

## Recognition signals
Not specified.

## Resolution method
1. The flag is **not** in the HTML → look at the **response headers**.
2. `curl -I http://inspect-me.chal.sigpwny.com/` (or `-D -`) → custom header: `Flag7: flag{7_n3tw0rk_mag1c}`.
3. Browser: DevTools → **Network** tab → request → **Response Headers**.

## Flag
flag{7_n3tw0rk_mag1c}

## Lessons and reusable patterns
- “Inspect” a page ≠ only the HTML: also check HTTP headers, cookies (Set-Cookie), JS/CSS, comments, robots.txt.
- Here: flag 7 = Flag7 header (“n3tw0rk_mag1c”); flag 6 = cookie Set-Cookie: flag=flag{6_1ns1d3_th3_c00k13_j4r} (URL-encoded).
- curl -I/-D - to see headers on the command line.
