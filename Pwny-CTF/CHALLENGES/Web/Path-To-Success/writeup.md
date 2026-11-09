---
title: "Path-To-Success"
ctf: "Pwny-CTF"
category: "web"
difficulty: "Not specified"
points: 50
techniques: ["encoding"]
tools: ["xxd", "curl", "cyberchef", "bash"]
keywords: ["Path-To-Success", "Pwny-CTF", "web", "encoding", "xxd", "curl", "cyberchef", "bash", "http", "hex"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Web/Path-To-Success/notes.md"
---

# Path-To-Success (Pwny-CTF, web)

## Summary
Challenge **Path-To-Success** from the Pwny-CTF CTF, web category. Main technique: encoding. Inspect the source (HTML comments, headers, robots.txt, JS) above all: indices/paths

## Statement and artefacts
Find the path to success (the flag). Directions are hidden somewhere [here](http://path-to-success.chal.sigpwny.com/)

Flag format: `sigpwny{...}`

“Find the path to success (the flag). The directions are hidden somewhere in here. »

**Provided files / artifacts:**
- `work/path-to-success.chal.sigpwny.com (file, 274 B)`

## Recognition signals
Not specified.

## Resolution method
1. **The reasoning**

In the **HTML source** of the page (`curl` / inspector), two comments:
```html
<!-- Flags are in the /6469726563746f7279 directory! -->
<!-- File is called '666c61670.txt' -->
```
(`6469726563746f7279` = hex of “directory”, `666c6167` = “flag”). The path is **literally** as written (the folder/file names ARE these hex strings):
```
/6469726563746f7279/666c61670.txt
```
→ `sigpwny{f1nD_y0Ur_sU$s3$s}`.

## Solve script
Script path: [scripts/solve.sh](scripts/solve.sh)

## Flag
sigpwny{f1nD_y0Ur_sU$s3$s}

## Lessons and reusable patterns
- Inspect the source (HTML comments, headers, robots.txt, JS) above all: indices/paths
- Decode the hex blobs (xxd -r -p, CyberChef) to understand, but the actual path may be the
