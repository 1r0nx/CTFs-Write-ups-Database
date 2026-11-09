---
title: "Cowsay-As-A-Service-CAAS"
ctf: "Pwny-CTF"
category: "web"
difficulty: "Not specified"
points: 75
techniques: ["substitution-cipher", "command-injection"]
tools: ["python"]
keywords: ["Cowsay-As-A-Service-CAAS", "Pwny-CTF", "web", "substitution-cipher", "command-injection", "http"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Web/Cowsay-As-A-Service-CAAS/notes.md"
---

# Cowsay-As-A-Service-CAAS (Pwny-CTF, web)

## Summary
Challenge **Cowsay-As-A-Service-CAAS** from the Pwny-CTF CTF, web category. Main technique: substitution-cipher. The flag: sigpwny{the_c0w_said_too_much}

## Statement and artefacts
Check out this sweet website that will say anything you give it! Can you get the flag in "/flag.txt"?

http://caas.chal.sigpwny.com

Note: `cowsay` will not return anything if given a blank input.

**author**: Pete

**Provided files / artifacts:**
- `work/Dockerfile (file, 312 B)`
- `work/index.html (file, 982 B)`
- `work/info.txt (text, 57 B)`

## Recognition signals
- Signal: chal.py, route /cowsay: JSON input is inserted into the command and then executed via os.popen.
- Signal: The quotation marks "." around input do not protect: in bash, the command substitution $(.) is also evaluated inside double quotes.

## Resolution method
1. Read the source → the entry goes into `os.popen` in double quotes → inject via `$(...)`.
2. Send as `input`: `$(cat /flag.txt)` → bash executes `cat /flag.txt`, the result replaces the text, and the cow “says” the flag in the JSON response.

1. **Flaw (source)**

`chal.py`, route `/cowsay`: JSON entry `input` is inserted into the command and then executed via `os.popen`:
```python
command = f'/usr/games/cowsay "{input}"'
output = os.popen(command).read()
```
The quotes `"..."` around `input` do not protect: in bash, the **command substitution** `$(...)` is also evaluated inside the double quotes.

## Flag
sigpwny{the_c0w_said_too_much}

## Lessons and reusable patterns
- Double quotes do not neutralize $(...) nor... in bash (only single quotes would). Hence the injection despite "{input}".
- The input goes through JSON ({"input": "$(cat /flag.txt)"}), not through a classic form field -> look at how the front calls the API.
- Same family as Shiny Button: user input -> shell command. Reflex $(...) as soon as we see os.popen/system/shell_exec.
