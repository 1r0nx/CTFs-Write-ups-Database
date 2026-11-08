---
title: "Stillwell-Estates"
ctf: "2026-hiCTF"
category: "web"
difficulty: "Not specified"
points: null
techniques: ["path-traversal", "file-inclusion", "encoding"]
tools: ["python"]
keywords: ["Stillwell-Estates", "hiCTF", "web", "path-traversal", "file-inclusion", "encoding", "python", "https", "lfi"]
status: "solved"
has_script: true
source: "hiCTF/Web/Stillwell-Estates/notes.md"
---

# Stillwell-Estates (hiCTF, web)

## Summary
Challenge **Stillwell-Estates** from the hiCTF CTF, web category. Main technique: path-traversal. Path.resolve / os.path.join + user input = absolute path trap: an absolute path overwrites the base. Filtering.. does NOT protect; verify that the resolved path starts with the authorized folder.

## Statement and artefacts
Not specified.

## Recognition signals
- Signal: The site is a SPA; all logic is in /assets/app.js. Endpoints identified including /api/agency/import/preview (agents /agency portal).
- Signal: The import studio accepts a partner export compressed in Brotli: compressed JSON body, headers Content-Type: application/json + Content-Encoding: br.
- Signal: Decompressed sample archive /assets/sample-export.br (python brotli module).
- Signal: The filter only rejects the substring.
- Signal: Or path.resolve(base, absolute_path) completely ignores base: path.resolve(PARTNER_DOCS, "/etc/passwd") -> /etc/passwd.
- Signal: ⇒ any absolute file is readable, without ever writing.

## Resolution method
1. `work/solve.py` — builds the manifest, compresses in Brotli, POST, and reads an arbitrary path. Usage: `python3 -I work/solve.py /tmp/stillwell-private/escrow-ledger.txt`

2. **Recognition**

- The site is a SPA; all logic is in `/assets/app.js`. Endpoints identified including **`/api/agency/import/preview`** (agent portal `/agency`).
- The import studio accepts a **compressed partner export in Brotli**: compressed JSON body, headers `Content-Type: application/json` + `Content-Encoding: br`.
- Decompressed `/assets/sample-export.br` example archive (python module `brotli`):
  ```json
  {"format":"stillwell.agency-export/1",
   "properties":[{"title":"Meadow House","neighborhood":"Greenpoint","price":990000,"document":"welcome.txt"}]}
  ```
→ each property can attach a **`document` = file name**; the server returns one **`excerpt`**.

3. **The flaw (confirmed in server.js, read via the LFI itself)**

```js
function resolvePartnerDoc(name){
  if (name.length > 512 || name.includes('..')) return { error: 'document path is not permitted' };
  const abs = path.resolve(PARTNER_DOCS, name);          // PARTNER_DOCS = __dirname/data/partner-docs
  return { name, excerpt: fs.readFileSync(abs,'utf8').slice(0,8192) };
}
```
- The filter **only rejects the `..` substring**.
- But **`path.resolve(base, absolute_path)` completely ignores `base`**: `path.resolve(PARTNER_DOCS, "/etc/passwd")` → `/etc/passwd`.
- ⇒ **any absolute file** is readable, without ever writing `..`.
- Proof by tests: `../welcome.txt` → *“document path is not permitted”*; **`/etc/passwd` → returned content**.
- Note: for static assets, the code nevertheless validates `abs.startsWith(PUBLIC+sep)` — this check is missing here.

4. **From bug to flag**

Successive absolute readings:
1. `/etc/passwd` → confirms the primitive (user `node`, uid 1000).
2. `/proc/self/environ` → `SECRET_DIR=/tmp/stillwell-private`, `PWD=/opt/stillwell`, and `RCTF_FLAG=hiCTF{...}` **always present** (see trap).
3. `/proc/self/cwd/server.js` → source code: the flag is written at startup in `${SECRET_DIR}/escrow-ledger.txt`, then `delete process.env.RCTF_FLAG`.
4. **`/tmp/stillwell-private/escrow-ledger.txt`** → the “restricted escrow ledger”:
   ```
   STILLWELL REALTY — RESTRICTED ESCROW LEDGER
   ...
   Closing authorization: hiCTF{s1l3nt_l4n73rn_3573735_12081388db}
   ```

## Solve script
Script path: `scripts/solve.py`

## Flag
hiCTF{s1l3nt_l4n73rn_3573735_12081388db}

## Lessons and reusable patterns
- path.resolve / os.path.join + user input = absolute path trap: an absolute path overwrites the base. Filtering.. does NOT protect; verify that the resolved path starts with the authorized folder.
- As soon as we have an absolute file reading, aim for /proc/self/environ (secrets + flag sometimes), /proc/self/cmdline, /proc/self/cwd/<f> (source code without guessing the path).
- Funny trap: delete process.env.RCTF_FLAG does not modify /proc/self/environ, which is the frozen snapshot at startup -> the "deleted" secret remained readable.
- Recognize this type: upload of an export/manifest which references documents by name, with extract preview.
