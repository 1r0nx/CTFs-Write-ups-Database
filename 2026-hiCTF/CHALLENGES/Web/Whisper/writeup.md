---
title: "Whisper"
ctf: "2026-hiCTF"
category: "web"
difficulty: "Not specified"
points: null
techniques: ["password-cracking", "jwt", "encoding"]
tools: ["python"]
keywords: ["Whisper", "hiCTF", "web", "password-cracking", "jwt", "encoding", "python", "hex", "nonce", "oracle"]
status: "solved"
has_script: true
source: "hiCTF/Web/Whisper/notes.md"
---

# Whisper (hiCTF, web)

## Summary
Challenge **Whisper** from the hiCTF CTF, web category. Main technique: password-cracking. MongoDB ($ne, $regex). The $regex becomes a Boolean oracle to exfiltrate the secret character by character, then forge the HMAC signature of the internal endpoint.

## Statement and artefacts
MongoDB ($ne, $regex). The $regex becomes a Boolean oracle to exfiltrate the secret character by character, then forge the HMAC signature of the internal endpoint.

## Recognition signals
- Signal: a client_secret compared without type checking allows operator injection.
- If we look at Two clients (/clients), think of public-web (scope read), report-signer (read, report:export).
- If we observe POST /api/token: {client_id, client_secret}, think of token (Bearer).
- If we observe POST /internal/export, think of scope report:export, authenticated by signature (no Bearer).
- Signal: The “signature mismatch” error describes the format of string_to_sign (strong index).
- Signal: The secret is compared like clients.findOne({client_id, client_secret}) without forcing the type -> we can pass an object like client_secret.

## Resolution method
1. **Blind exfiltration (blind regex)**

Oracle: **token issued** = the regex matches the secret. Procedure (`work/leak.py`):
1. Length: `{"$regex":"^.{N}$"}` until match → **32** characters.
2. Prefix: for each character of `[0-9a-f...]`, test `{"$regex":"^"+prefix+c}`; keep whoever matches. (think of **escape** the character: `re.escape`). → secret of `report-signer` = **`695b1227aef115c297f0db3780c420f2`** (16 bytes, hex).

2. **Forge of the signature**

- `string_to_sign` = `METHOD \n PATH \n CANONICAL_QUERY \n HEX_SHA256(body) \n X-Timestamp` with **real line breaks** (`\n`), empty `CANONICAL_QUERY` = empty line, empty `body` → `HEX_SHA256("") = e3b0c442…`.
- **Anti-replay trap**: once the signature is valid, the error reveals that **one more line** is needed: add a `X-Nonce` header (single value) **and** add it as the 6th line of `string_to_sign`, then re-sign.
- Final string (6 lines):
  ```
  POST
  /internal/export

  <sha256(body)>
  <timestamp>
  <nonce>
  ```
`X-Signature = hex(HMAC-SHA256(secret, string_to_sign))`, + `X-Client-Id/X-Timestamp/X-Nonce` headers. → `200 {"ok":true,"report":"export authorized","flag":"hiCTF{...}"}`.

3. **Recognition**

- Two clients (`/clients`): `public-web` (scope `read`), `report-signer` (`read`, `report:export`).
- `POST /api/token`: `{client_id, client_secret}` → token (Bearer).
- `POST /internal/export`: scope `report:export`, **authenticated by signature** (no Bearer). Headers `X-Client-Id`, `X-Timestamp` (±300 sec), `X-Signature` = `hex(HMAC-SHA256(client_secret, string_to_sign))`. The `client_id` is **trim** before lookup.
- The “signature mismatch” error describes the format of `string_to_sign` (strong index).

4. **The flaw: NoSQL injection on /api/token**

The secret is compared like `clients.findOne({client_id, client_secret})` without forcing the type → we can pass an **object** like `client_secret`:
```
{"client_id":"report-signer","client_secret":{"$ne":null}} -> token issued (bypass auth)
{"client_id":"report-signer","client_secret":{"$regex":"^695b..."}} -> SSI token the secret match
```
(`$gt`/`$exists` returns "invalid" here, but `$ne` and `$regex` pass.)

## Solve script
Script path: `scripts/leak.py`
Script path: `scripts/solve.py`

## Flag
hiCTF{bl1nd_regex_3xfil_then_f0rge_the_cust0m_s1gner_1aa2d6a999}

## Lessons and reusable patterns
- Recognize: an auth parameter that accepts a JSON object ({"$ne":…}) = NoSQL injection.
- An anchored $regex (^prefix) transforms a login into a secret exfiltration oracle.
- For a “house” signature: recovering the secret is enough; read the error messages that
- Tracks ruled out (all negative): brute-force rockyou/JWT, secrets derived from id (sha256…),
