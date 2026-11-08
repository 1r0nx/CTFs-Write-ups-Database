---
title: "Shiny-Button"
ctf: "Pwny-CTF"
category: "web"
difficulty: "Not specified"
points: 150
techniques: ["substitution-cipher", "command-injection"]
tools: ["php"]
keywords: ["Shiny-Button", "Pwny-CTF", "web", "substitution-cipher", "command-injection", "php", "http"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Web/Shiny-Button/notes.md"
---

# Shiny-Button (Pwny-CTF, web)

## Summary
Challenge **Shiny-Button** from the Pwny-CTF CTF, web category. Main technique: substitution-cipher. The flag: sigpwny{4lL_tH4T_g1it1eRS_iS_G0lD}

## Statement and artefacts
Click [here](http://shiny-button.chal.sigpwny.com) to learn more about MD5 hashing!

Take a look at the source code of what's running on the page. The page uses some insecure methods get the job done. See if you can exploit it and get the flag.

Flag format: `sigpwny{...}`

**Provided files / artifacts:**
- `work/info.txt (text, 69 B)`
- `work/shiny-button.chal.sigpwny.com (file, 1.5 KB)`

## Recognition signals
- Signal: index.php constructs a shell command with the GET string parameter without any validation.
- Signal: Everything we put in string is injected into a real command line on the server side.

## Resolution method
1. Locate in the source that the entry leaves as is in `shell_exec` → command injection.
2. List the folder to find the flag — field: `$(ls );hash me!` → `$(...)` = **command substitution**: its result replaces the text before `md5sum`. Reveals `secret_cave/`.
3. Read the flag — field: `$(cat secret_cave/flag.txt);hash me!` → `;` separates two commands; the content of the flag is displayed on the page.

1. **Flaw (source)**

`index.php` constructs a shell command with the GET parameter `string` without any validation:
```php
echo shell_exec('echo '.$_GET['string'].' | md5sum');
```
Everything we put in `string` is injected into a real command line on the server side.

## Solve script
Script path: `scripts/index.php`

## Flag
sigpwny{4lL_tH4T_g1it1eRS_iS_G0lD}

## Lessons and reusable patterns
- Command injection: as soon as a user entry ends in shell_exec/system/exec without escape, we exit the intended command with $(...),...,;, &&, |.
- Reflex: first map ($(ls), $(pwd)) before reading — the flag was not in a guessable path (secret_cave/).
- The | md5sum final does not interfere: $(...) is evaluated before the pipe, and; clean cut.
