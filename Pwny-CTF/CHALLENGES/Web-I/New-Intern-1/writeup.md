---
title: "New-Intern-1"
ctf: "Pwny-CTF"
category: "web"
difficulty: "Not specified"
points: 50
techniques: []
tools: ["curl"]
keywords: ["New-Intern-1", "Pwny-CTF", "web", "curl", "http"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Web-I/New-Intern-1/notes.md"
---

# New-Intern-1 (Pwny-CTF, web)

## Summary
Challenge **New-Intern-1** from the Pwny-CTF CTF, web category. Client-side security = no security: password and logic are visible in the JS.

## Statement and artefacts
In order to save server compute resources, I moved the login check to the front end. Good thing they gave me prod access so I can save our company money!!

Can you find the passcode and login?

http://new-intern-1.chal.sigpwny.com

**author**: Pete

## Recognition signals
Not specified.

## Resolution method
1. Read the JS of the page (`util.js` + inline script). The verification is client-side:

```js
   if (document.getElementById("passcode").value == "hunter1") {
       location.href = getNextPage(...)   // getNextPage(x) = md5(x) + ".html"
   }
   ```

2. The passcode is **hard**: `hunter1`.
3. The “next” page = `md5("hunter1") + ".html"` = `726ad07bc398372b56a52e3de8693679.html`.
4. Retrieve this page → `sigpwny{i_put_java_not_javascript_on_my_resume}` (either by typing the passcode in the form, or `curl http://new-intern-1.chal.sigpwny.com/726ad07b...html`).

## Flag
sigpwny{i_put_java_not_javascript_on_my_resume}

## Lessons and reusable patterns
- Client-side security = no security: password and logic are visible in the JS.
- util.js was an MD5 implementation; getNextPage(x) = md5(x)+".html" -> calculate the hash to find the hidden URL.
- Reflex: read all scripts (inline + external) of a login page.
