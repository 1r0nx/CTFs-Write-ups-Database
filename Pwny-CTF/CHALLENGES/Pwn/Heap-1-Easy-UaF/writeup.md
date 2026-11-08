---
title: "Heap-1-Easy-UaF"
ctf: "Pwny-CTF"
category: "pwn"
difficulty: "easy"
points: 350
techniques: ["heap-use-after-free", "tcache-poisoning"]
tools: ["netcat", "python"]
keywords: ["Heap-1-Easy-UaF", "Pwny-CTF", "pwn", "heap-use-after-free", "tcache-poisoning", "netcat", "python", "uaf", "tcache", "heap"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Pwn/Heap-1-Easy-UaF/notes.md"
---

# Heap-1-Easy-UaF (Pwny-CTF, pwn)

## Summary
Challenge **Heap-1-Easy-UaF** from the Pwny-CTF CTF, pwn category. Main technique: heap-use-after-free. Recognize: free without ptr=NULL + two objects of the same size, one of which has controlled content

## Statement and artefacts
This is nearly identical to heap 0, however users are logged out before being deleted. Can you find another way to become 'admin'?

`nc chal.sigpwny.com 1360`

Multi-user terminal. `user_t { char name[60]; uint32_t logged_in; }` (64 B) and `document_t { char text[64]; }` (64 B) → **same cache class (0x40)**. `users[0]`=admin (logged_in=0, inaccessible), `users[1]`=sigpwny (current). Goal: become `current_user` with `name=="admin"` for `shell`.
- `shell` only tests **only the name** (`strncmp(users[current_user]->name,"admin")`), not `logged_in`.
- `switch_user(id)` requires `users[id]->logged_in!= 0`.
- `create_doc` = **`calloc`** → resets the reoccupied chunk.

**Provided files / artifacts:**
- `work/heap1 (file, 27.8 KB)`
- `work/heap1_patched (file, 32.0 KB)`
- `work/ld-2.31.so (library, 187.0 KB)`
- `work/libc-2.31.so (library, 7.1 MB)`
- `work/libc.so.6 (file, 7.1 MB)`

## Recognition signals
- If we observe del_user releases the chunk but does not make users[arg1]=NULL, think of ghost pointer (UaF).
- Signal: The chunk returns to the 0x40 cache and will be returned to the next object 64 B (a document) -> users[id] and documents[j] alias the same memory.

## Resolution method
1. **Method (resolve actually played)**

1. `create_user ir0nx` → `users[2]`, logged_in=1.
2. `del_user 2` → chunk freed, `users[2]` ghost.
3. `create_doc` → `calloc` takes over the chunk (reset to 0).
4. `write_doc 0 <payload>` with **64 bytes**: `b"admin" + \0*55 + p32(1)` → writes `name="admin"` AND `logged_in=1` (offset 60). Writing goes through `memcpy(..., arg1_len)` → null bytes / `\x01` are copied as is (input read in binary, not string).
5. `switch_user 2` → `logged_in` is 1 → `current_user=2`, name="admin".
6. `shell` → `system("/bin/sh")` → `cat flag.txt`. Script: `work/pwny.py --remote --host chal.sigpwny.com --port 1360`.

2. **Heap-0 difference -> Heap-1 (the real subtlety)**

Only one functional addition in Heap-1: `users[arg1]->logged_in = 0;` **just before** `free`. The UaF (non-NULL pointer) is **identical**; what changes is the state of the freed chunk.
- **Heap-0**: `logged_in` remains 1 after `free` → “baby” path: `switch_user` **to the freed user directly** (before any reoccupation), then document to overwrite **only the name**. We never write `logged_in`.
- **Heap-1**: `logged_in=0` before `free` → this path is blocked (`switch` responds *"That user isn't logged in"*). You must **reoccupy first** with a document and **rewrite `logged_in=1` yourself**, then `switch`.

My payload (name + `logged_in=1`, switch *after* reoccupancy) is the **general version**: it works on both. On Heap-0 the `logged_in=1` part was redundant; on Heap-1 it is essential. (Empirically verified: sequence “name only + switch before reoccupancy” = shell on Heap-0, failure on Heap-1.)

3. **Flaw**

`del_user` releases the chunk **but does not do `users[arg1]=NULL`** → ghost pointer (UaF). The chunk returns to the 0x40 cache and will be returned to the next object 64 B (a document) → `users[id]` and `documents[j]` **alias** the same memory.

## Solve script
Script path: `scripts/pwny.py`

## Flag
sigpwny{wdym_1_sh0uld_set_v4rs_t0_null_wh3n_freed}

## Lessons and reusable patterns
- Recognize: free without ptr=NULL + two objects of the same size, one of which has controlled content
- calloc (≠ malloc) zero the reused chunk -> any field not rewritten by the attacker starts at 0
- Always look at what the final check really tests (here the name alone): this changes the minimum payload.
- Same binary/flaw can have several exploitable states depending on the order of operations
