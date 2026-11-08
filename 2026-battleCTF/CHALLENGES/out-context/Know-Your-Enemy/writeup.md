---
title: "Know-Your-Enemy"
ctf: "2026-battleCTF"
category: "misc"
difficulty: "Not specified"
points: 26
techniques: ["osint", "git-forensics"]
tools: ["curl", "git"]
keywords: ["Know-Your-Enemy", "battleCTF", "misc", "osint", "git-forensics", "curl", "git", "https"]
status: "solved"
has_script: false
source: "battleCTF/CHALLENGES/out-context/Know-Your-Enemy/notes.md"
---

# Know-Your-Enemy (battleCTF, misc)

## Summary
Challenge **Know-Your-Enemy** from the battleCTF CTF, misc category. Main technique: osint. Git commit metadata (name/email user.name/user.email) often leaks a contributor's real name, even when their GitHub handle is anonymous.

## Statement and artefacts
Before you attack a target, you study it. BUG|PWN has a public footprint like any other security team. There's a website, a GitHub organization, and a handful of social accounts. Everything you need for this challenge is already public. Nothing here needs to be brute forced, guessed, or bought.

Someone who has contributed to BUG|PWN's work left their real name somewhere in this footprint, even though they go by a handle everywhere else. Find their surname.

Flag format: `CTF{surname}`.

No brute forcing, no credential attacks, no social engineering of real people, and no contacting anyone you find during your research. Everything you need to solve this is already public.

Public footprint of the **BUG|PWN** team (site + GitHub + networks). A contributor to their work left his **real name** somewhere, while he uses a **handle everywhere else**. Find his **last name**. Format: `CTF{surname}`. Nothing to brute force: everything is public.

**Provided files / artifacts:**

## Recognition signals
- Signal: Git commit metadata (name/email user.name/user.email) often leaks a contributor's real name, even when their GitHub handle is anonymous.
- Signal: GitHub: github.com/0xbugpwn · Site: bugpwn.com · X: @bug_pwn · LinkedIn: company/0xbugpwn.
- Signal: Founder: Sadoc Adonon. Target contributor: handle namalanga, email commit sohoueto@tutamail.com.

## Resolution method
1. **Path of reasoning (precise)**

1. **Entry point** = GitHub page `github.com/0xbugpwn` (provided/found via the site).
2. **Nature of account**: the org endpoint returns 404 → it is a **user account**, not an org.
   ```bash
   curl -s https://api.github.com/users/0xbugpwn | jq '{login,name,blog,twitter_username,public_repos}'
   # -> login=0xbugpwn, name="BUG|PWN", blog=bugpwn.com, twitter=bug_pwn, 6 repos
   ```
3. **List repos** (6): conference, THEARENA, NICC-2026-CTF, battleCTF-2023, AfricabattleCTF2024, VulnerabilityResearch.
   ```bash
   curl -s "https://api.github.com/users/0xbugpwn/repos?per_page=100" | jq -r '.[].name'
   ```
4. **Find contributor ≠ 0xbugpwn**: scan contributors + commit authors from each repo. All = `0xbugpwn`, **except THEARENA** which has a 2nd contributor: the handle **`namalanga`**.
   ```bash
   for r in VulnerabilityResearch conference THEARENA NICC-2026-CTF battleCTF-2023 AfricabattleCTF2024; do
     curl -s "https://api.github.com/repos/0xbugpwn/$r/contributors" | jq -r '.[]?.login'
   done
   ```
5. **Read the commit metadata of `namalanga`** (the git name ≠ the GitHub login):
   ```bash
   curl -s "https://api.github.com/repos/0xbugpwn/THEARENA/commits?per_page=100" \
     | jq -r '.[]? | "\(.commit.author.name) <\(.commit.author.email)> | gh:\(.author.login)"' | sort -u
   # -> namalanga <ZXQPH0QXZ> | gh:namalanga
   ```
6. **Confirm that `namalanga` = handle everywhere**: GitHub profile without `name`, its site `namalanga.github.io` = just a battleCTF archive (no name), no web results. The **only** place where a real name appears = the commit email → **`sohoueto`**.
7. **Rule out the founder**: the site/LinkedIn shows **Sadoc Adonon** ("SADOC A.", founder), but he uses his real name **openly** → he is not the target (who is hiding behind a handle). The target is indeed `namalanga` → last name **Sohoueto**.
8. **Flag**: `CTF{sohoueto}` (lower case, exactly like in the email; the `CTF{...}` wrapper is imposed by the statement, not guessed).

2. **BUG|PWN public fingerprint (reference)**

- GitHub: `github.com/0xbugpwn` · Website: `bugpwn.com` · X: `@bug_pwn` · LinkedIn: `company/0xbugpwn`
- Founder: Sadoc Adonon. Target contributor: handle `namalanga`, email commit `sohoueto@tutamail.com`.

## Flag
CTF{sohoueto}

## Lessons and reusable patterns
- Recognize this type: OSINT “team/person”, mention of a contributor + handle -> think
- API reflex (without auth, 60 req/h): users/<u> -> repos -> repos/<u>/<r>/contributors ->
- An unexpected contributor on a single repo (here THEARENA) is the strong signal.
- Trap: do not confuse the displayed founder (Sadoc Adonon, public name) with the target
- 0xbugpwn is a user account, not an org (404 on /orgs/) -> use /users/.
