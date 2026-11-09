---
title: "JS-Jail"
ctf: "Pwny-CTF"
category: "misc"
difficulty: "Not specified"
points: 300
techniques: ["jail-escape", "pyjail"]
tools: ["pwntools", "netcat", "nodejs", "python"]
keywords: ["JS-Jail", "Pwny-CTF", "misc", "jail-escape", "pyjail", "pwntools", "netcat", "nodejs", "python"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Jail/JS-Jail/notes.md"
---

# JS-Jail (Pwny-CTF, misc)

## Summary
Challenge **JS-Jail** from the Pwny-CTF CTF, misc category. Main technique: jail-escape. JSFuck relies on JS coercion:![]->false,!![]->true, +[]->0, +!![]->1,

## Statement and artefacts
Sometimes web dev can feel like you're in jail.

`nc chal.sigpwny.com 7009`

**author**: Cameron

Server `nc chal.sigpwny.com 7009`, `chal.js` provided:
- filter `/^[\[\]()!+]+$/` → the entry can only contain **only** `[ ] ( )! +`;
- wins if `eval(message) == "gimme the flag"`. You therefore need a JS expression using only these 6 characters and **whose result is** the string `"gimme the flag"`.

**Provided files / artifacts:**

## Recognition signals
- If we observe ⚠️ “eval source” trap (the heart of the challenge), think about by default jsfuck.com wraps in eval(“…”).
- If we observe gigantic Payload, always remember to pwntools (sendlineafter), nc raw truncates (hint provided).

## Resolution method
1. Read `chal.js` → identify the constraint (6 characters) and the target (`eval(...) == "gimme the flag"`).
2. Recognize **JSFuck** (clues: “string with `[]()!+`”, jsfuck.com).
3. On **jsfuck.com**: type `gimme the flag`, **uncheck “eval source”**, copy the output.
4. Send with **pwntools** (payload too long for raw nc): `io.sendlineafter(b'... ', msg)` then `io.interactive()`. Script: `work/solve.py`.

## Solve script
Script path: [scripts/chal.js](scripts/chal.js)
Script path: [scripts/solve.py](scripts/solve.py)

## Flag
sigpwny{over_one_billion_websites_use_javascript}

## Lessons and reusable patterns
- JSFuck relies on JS coercion:![]->false,!![]->true, +[]->0, +!![]->1,
- ⚠️ “eval source” trap (the heart of the challenge): by default jsfuck.com wraps in eval(“…”),
- Gigantic payload -> always pwntools (sendlineafter), raw nc truncates (hint provided).
- Recognize this type: JS jail, charset reduced to []()!+ (or []()!+{}), target = produce a
