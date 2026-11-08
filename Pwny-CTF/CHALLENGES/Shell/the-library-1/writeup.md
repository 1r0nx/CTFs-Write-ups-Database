---
title: "the-library-1"
ctf: "Pwny-CTF"
category: "misc"
difficulty: "Not specified"
points: 50
techniques: ["format-string", "git-forensics"]
tools: ["git"]
keywords: ["the-library-1", "Pwny-CTF", "misc", "format-string", "git-forensics", "git", "zip", "https"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Shell/the-library-1/notes.md"
---

# the-library-1 (Pwny-CTF, misc)

## Summary
Challenge **the-library-1** from the Pwny-CTF CTF, misc category. Main technique: format-string. Reflex: as soon as there is a.git/, search the history — git log, git log -p (diffs), git show <commit>, git stash list, branches (--all).

## Statement and artefacts
I have an interesting zip that you need to find, it's up on my git account. There is an interesting message attached to the commit. That's the flag for this challenge!

https://github.com/Thomas-Quig/SIGPwny-Chals-FA2020

## Recognition signals
Not specified.

## Resolution method
1. The folder contains a git repository (`.git/`).
2. Read history: `git log` (or `git log --all --format='%s%n%b'`).
3. The flag is in the **commit body** `03c08c8` (“Added files via upload”): `sigpwny{git_those_pwnypoints}` (verified: identical to flag.txt).

## Flag
sigpwny{git_those_pwnypoints}

## Lessons and reusable patterns
- Reflex: as soon as there is a.git/, search the history — git log, git log -p (diffs), git show <commit>, git stash list, branches (--all).
- Secrets/flags often hang around in old commits, commit messages, or deleted files but still in the history.
- Pun: “git those pwnypoints” = get those points.
