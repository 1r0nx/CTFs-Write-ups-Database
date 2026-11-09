---
title: "Budget-Dalle"
ctf: "Pwny-CTF"
category: "web"
difficulty: "Not specified"
points: 100
techniques: ["path-traversal"]
tools: ["python"]
keywords: ["Budget-Dalle", "Pwny-CTF", "web", "path-traversal", "png", "jpg", "http"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Web/Budget-Dalle/notes.md"
---

# Budget-Dalle (Pwny-CTF, web)

## Summary
Challenge **Budget-Dalle** from the Pwny-CTF CTF, web category. Main technique: path-traversal. The flag: sigpwny{lat3nt_space_in_neural_n3t}

## Statement and artefacts
I made my own tile model! It only works on a couple animals though:/

Can you get read /flag.txt on the server?

http://budget-dalle.chal.sigpwny.com

**author**: Pete

**Provided files / artifacts:**
- `work/Dockerfile (file, 301 B)`
- `work/budget-dalle.chal.sigpwny.com (file, 496 B)`
- `work/info.txt (text, 92 B)`

## Recognition signals
- Signal: chal.py, route /file: the name parameter is stuck to a path, and as a last resort served without extension.
- If we observe No normalization, thinking of name=././././flag.txt takes it out of the files/assets/ folder.
- Signal: Path traversal: a parameter which is used to construct a file path +./ = arbitrary reading. Put “enough”./ (one./ too much has no effect, we still reach /).
- Signal: Classic trap: the isfile(name + '.jpg') check fails for the flag, but the fallback without extension does not check anything -> this is the usable path.

## Resolution method
1. Read the source → the page displays `<img src="/file?name=cat">`; the `/file` route serves a file by name.
2. GB up the tree to the root — URL: `http://budget-dalle.chal.sigpwny.com/file?name=../../../../flag.txt` → `send_file('files/assets/../../../../flag.txt')` resolves to `/flag.txt`, served as is.

1. **Flaw (source)**

`chal.py`, route `/file`: the `name` parameter is stuck to a path, and as a last resort served **without extension**:
```python
name = request.args.get('name')
if os.path.isfile('files/assets/' + name + '.jpg'): ...
elif os.path.isfile('files/assets/' + name + '.png'): ...
return send_file('files/assets/' + name)   #<- no filter on../
```
No normalization: `name=../../../../flag.txt` takes out of the `files/assets/` folder.

## Flag
sigpwny{lat3nt_space_in_neural_n3t}

## Lessons and reusable patterns
- Path traversal: a parameter which is used to construct a file path +../ = arbitrary reading. Put “enough”../ (one../ too much has no effect, we still reach /).
- Classic trap: the isfile(name + '.jpg') check fails for the flag, but the fallback without extension does not check anything -> this is the usable path.
- Reflex: any route?name=,?file=,?path= -> test../../../../etc/passwd or.../flag.txt.
