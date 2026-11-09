---
title: "New-Intern-2"
ctf: "Pwny-CTF"
category: "web"
difficulty: "Not specified"
points: null
techniques: ["encoding", "reverse-engineering"]
tools: []
keywords: ["New-Intern-2", "Pwny-CTF", "web"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Web-I/New-Intern-2/notes.md"
---

# New-Intern-2 (Pwny-CTF, web)

## Summary
Challenge **New-Intern-2** from the Pwny-CTF CTF, web category. Client-side security = no security: everything the browser executes is visible and editable. Always read the JS of a “login” page before looking further.

## Statement and artefacts
**Provided files / artifacts:**
- `info.txt (text, 313 B)`

## Recognition signals
Not specified.

## Resolution method
1. Open the page and read the verification JavaScript (dev tools → Sources). The algo compares the input to a value `target`, modifying each character according to a **Fibonacci** type sequence.
2. **Reverse** the operation: to find the passcode, we subtract the same sequence from the character codes of `target`. Script executed in the **console** (`info.txt`):

```js
   let target = '256<guv\x9A\xA6\xCB';
   let passcode = '';
   let a = 1, b = 1, c = 0;
   for (let i = 0; i < target.length; i++) {
       passcode += String.fromCharCode(target.charCodeAt(i) - a); // we subtract a
       c = a; a += b; b = c;                                       // a, b advance in Fibonacci
   }
   document.getElementById("passcode").value = passcode;
   checkPasscode();
   ```

3. The passcode thus calculated is accepted → flag `sigpwny{so_when_will_i_get_promoted}`.

## Flag
sigpwny{so_when_will_i_get_promoted}

## Lessons and reusable patterns
- Client-side security = no security: everything the browser executes is visible and editable. Always read the JS of a “login” page before looking further.
- Recognize this type: the form validates the password without network request (everything happens in JS) -> reverse the algorithm.
- charCodeAt(character -> code) and String.fromCharCode(code -> character) are both tools for manipulating text character by character. \xNN = a byte written in hexadecimal.
- Tip: you can call the verification function (checkPasscode()) directly from the console instead of retyping the password.
