---
title: "Decision-Day-1"
ctf: "Pwny-CTF"
category: "web"
difficulty: "Not specified"
points: 50
techniques: []
tools: ["curl"]
keywords: ["Decision-Day-1", "Pwny-CTF", "web", "curl", "http"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Web-I/Decision-Day-1/notes.md"
---

# Decision-Day-1 (Pwny-CTF, web)

## Summary
Challenge **Decision-Day-1** from the Pwny-CTF CTF, web category. Web reflexes: HTML source + comments, CSS (display:none elements), JS (even obfuscated -> run it in console / DevTools), cookies & headers (DevTools -> Application / Network, or curl -I).

## Statement and artefacts
Congrats on being admitted to SIGPwny University! Can you find all the secret flags hidden inside the acceptance page?

Each flag is numbered 1-4 so you know which challenge to submit it for. For example, flag n would look like `sigpwny{n_flagcontenthere}`.

http://decision-day.chal.sigpwny.com

**author**: Emma

## Recognition signals
Not specified.

## Resolution method
1. **The 4 hideouts (page http://decision-day.chal.sigpwny.com/)**

1. **HTML Comment** (`Ctrl+U`) → `sigpwny{1_welcome_to_sigpwny_university!}`
2. **Hidden SVG** (`.flag2 { display:none }` in style.css) → `sigpwny{2_hidden_in_plain_sight}`
3. **JS obfuscated JSFuck** (script.js, `printFlag3()`) → `sigpwny{3_reading_the_fine_print}`
4. **Cookie** (`Set-Cookie: flag=...`, `{}` en `%7B/%7D`) → `sigpwny{4_i_hope_theyre_chocolate_chip}`

## Flag
sigpwny{1_welcome_to_sigpwny_university!}

## Lessons and reusable patterns
- Web reflexes: HTML source + comments, CSS (display:none elements), JS (even obfuscated -> run it in console / DevTools), cookies & headers (DevTools -> Application / Network, or curl -I).
- JSFuck = JS written with only []()!+; it runs normally — running it in the console prints the result.
- Decode a URL-encoded cookie: %7B={, %7D=}.
