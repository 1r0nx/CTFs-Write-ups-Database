---
title: "EchoGate"
ctf: "2026-battleCTF"
category: "web"
difficulty: "Not specified"
points: 136
techniques: ["http-request-smuggling", "encoding"]
tools: ["curl", "python"]
keywords: ["EchoGate", "battleCTF", "web", "http-request-smuggling", "encoding", "curl", "python", "http", "oracle"]
status: "solved"
has_script: true
source: "battleCTF/CHALLENGES/web/EchoGate/notes.md"
---

# EchoGate (battleCTF, web)

## Summary
Challenge **EchoGate** from the battleCTF CTF, web category. Main technique: http-request-smuggling. Target: 169.58.126.107:3005 — gateway (proxy) in front of a backend. Blackbox (Files: none). of the gateway, + backend which trusts X-Forwarded-For: 127.0.0.1 (loopback) for admin access.

## Statement and artefacts
EchoGate is a small internal API gateway: a public-facing proxy in front of a backend service that nobody is supposed to reach directly. The gateway only lets a narrow set of public routes through. Everything else is somebody else's problem.

- `work/solve.py`: full exploit (`python3 solve.py [/path]`), reusable `smuggle()` helper.

**Provided files / artifacts:**

## Recognition signals
- Signal: HTTP Request Smuggling CL.CL (double Content-Length) to bypass the allowlist.
- Signal: The gateway accepts a double Content-Length (a strict parser would return 400).
- Signal: Test: it retains the last CL for ITS reading but relays the complete body; the backend also retains the last CL to bound the body of /api/echo.
- Signal: the backend echoes "X", then parses the rest as a pipelined request on the keep-alive gateway↔backend connection -> we send any path outside /api/ directly to the backend (the gateway never saw it).
- Signal: Proof: GET /flag smuggled -> 404 from the backend (not found) instead of 403 from the gateway (path not allowed).
- Signal: The socket response contains 2 HTTP responses: the echo (200) then that of the backend to the smuggled request.

## Resolution method
1. **Mapping (black box)**

- **Gateway**: ONLY allows paths starting with **`/api/`** (otherwise `403 path not allowed`, `startsWith` strict: `/api`→403, `/apix`→403, `/x/api/echo`→403). It **relays the raw path** (oracle: `/api/../api/echo`→404, therefore **no normalization**; `/api/api/echo`→404, therefore **no prefix strip**). Rejects `Transfer-Encoding` → `400 ambiguous framing` (anti-smuggling TE).
- **Backend**: router with **exact match** on `req.url` (404 `not found` custom; `/api/echo?x`→404, `/api/echo/`→404). Routes seen: `/api/echo` (public, reflects body) and **`/admin/flag`** (internal).

2. **Method (summary)**

1. Map gateway (`startsWith('/api/')`, raw relay) vs backend (exact match) via statuses 403/404.
2. Confirm that the echo reflects the body (desync oracle).
3. TE blocked (`ambiguous framing`); **double CL accepted** → desync CL.CL (large CL first, small last).
4. Smuggler `GET /flag` → 404 backend = **gate bypassed**; enumerate → `/admin/flag` = 403 “internal origin”.
5. Re-smuggler `GET /admin/flag` with `X-Forwarded-For: 127.0.0.1` → **200 + flag**.

3. **Flaw 1 — bypass of the gateway by desync CL.CL**

The gateway **accepts a double `Content-Length`** (a strict parser would return 400). Test: she retains the **last** CL for HER reading *but* relays the complete body; the backend also retains the last CL to bound the body of `/api/echo`. In practice:
```
POST /api/echo HTTP/1.1
Host: ...
Content-Type: text/plain
Content-Length: <GRAND>      <- the gateway reads the whole body with it
Content-Length: 1           <- the backend only consumes 1 byte as body
Connection: keep-alive

X<SMUGGLED REQUEST>
```
→ the backend echo “X”, then **parse the rest as a pipelined request** on the keep-alive gateway↔backend connection → we send any path **except `/api/`** directly to the backend (the gateway has never seen it). Proof: `GET /flag` smuggled → **404 from the backend** (`not found`) instead of **403 from the gateway** (`path not allowed`). The socket response contains **2 HTTP responses**: the echo (200) then that of the backend to the smuggled request.

4. **Flaw 2 — admin access via X-Forwarded-For loopback**

`/admin/flag` (reached by smuggling) → `403 admin access requires internal origin`. The backend grants admin access if the request carries **`X-Forwarded-For: 127.0.0.1`** (it trusts the loopback declared in XFF). Other headers tested (`X-Internal`, `X-Real-IP`, `X-Origin`, `Host: localhost`, `X-Internal-Origin`…) → all 403. Only `X-Forwarded-For: 127.0.0.1` → **200 + flag**.

## Solve script
Script path: `scripts/solve.py`

## Flag
CTF{12de61a5e5def6eb9d565836bd461566}

## Lessons and reusable patterns
- Recognize: proxy/gateway + backend + endpoint which reflects the body -> think request smuggling
- curl is not enough (it normalizes/single request) -> raw socket in Python to control the
- A backend behind a proxy often trusts X-Forwarded-For/loopback for "internal":
- Desync signals: multiple HTTP responses on a connection, or a backend response (404/403
