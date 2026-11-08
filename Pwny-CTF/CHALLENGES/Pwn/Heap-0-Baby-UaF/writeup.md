---
title: "Heap-0-Baby-UaF"
ctf: "Pwny-CTF"
category: "pwn"
difficulty: "Not specified"
points: 300
techniques: ["heap-use-after-free", "git-forensics"]
tools: ["netcat", "python"]
keywords: ["Heap-0-Baby-UaF", "Pwny-CTF", "pwn", "heap-use-after-free", "git-forensics", "netcat", "python", "uaf", "heap"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Pwn/Heap-0-Baby-UaF/notes.md"
---

# Heap-0-Baby-UaF (Pwny-CTF, pwn)

## Summary
Challenge **Heap-0-Baby-UaF** from the Pwny-CTF CTF, pwn category. Main technique: heap-use-after-free. Use-After-Free — free() does not reset the pointer to NULL -> dangling pointer; reallocating the SAME size gives back the block -> two pointers (user ↔ document) alias the same memory -> we forge a user_t.

## Statement and artefacts
Welcome to heap exploitation!

This application is a multi-user terminal that allows you to be logged in as a number of users, and switch between them. You can also create & write text documents that belong to no particular user.

The goal is to become a user named 'admin' and activate the `shell` command.

For this first challenge, see if you can find a use after free vulnerability and exploit it!

`nc chal.sigpwny.com 1359`

- Multi-user terminal. `user_t { char name[60]; uint32_t logged_in; }` = **64 B**; `document_t { char text[64]; }` = **64 B** (the code `assert()` is equality!). **Same size → same allocator tray**.
- Purpose: to be connected under a user named `"admin"` then `shell` (`system("/bin/sh")`).
- Legally impossible: the real `admin` (user[0]) has `logged_in=0` (not switchable); recreate "admin" → "User exists already".

**Provided files / artifacts:**
- `work/heap0 (file, 31.8 KB)`
- `work/heap0_patched (file, 36.0 KB)`
- `work/ld-2.31.so (library, 187.0 KB)`
- `work/libc-2.31.so (library, 7.1 MB)`
- `work/libc.so.6 (file, 7.1 MB)`

## Recognition signals
- Signal: Use-After-Free — free() does not reset the pointer to NULL -> dangling pointer; reallocating the SAME size gives back the block -> two pointers (user ↔ document) alias the same memory -> we forge a user_t.
- Signal: 🪤 The trap I encountered (struct offsets): logged_in is at offset 60 (after name[60]), not 64. I had put (64-len(name))*b"\0" + logged_in -> logged_in fell at offset 64 (excluding struct, truncated by memcpy capped at 64) -> remained 0. Correct = (60-len(name))*b"\0" + p32(1). Always draw the struct and count the offsets.

## Resolution method
1. **Method (exploit)**

1. `create_user ir0nx` → user[2], `logged_in=1`.
2. `del_user 2` → `free`, but `users[2]` **still hangs** on the block (armed UaF).
3. `create_doc` → `calloc(64)` **reuses the freed block** → `documents[0]` and `users[2]` = **same memory** (calloc reset it to 0).
4. `write_doc 0 <payload>` → forge the user via the document:
   ```python
   payload = b"admin" + (60-len(b"admin"))*b"\0" + p32(1)   # name="admin" (offset 0-59) + logged_in=1 (offset 60)
   ```
5. `switch_user 2` → `logged_in`≠0 OK, `name`="admin".
6. `shell` → `strncmp(name,"admin")==0` → `system("/bin/sh")` → `cat flag.txt`.

2. **🐞 The bug (DEL_USER)**

```c
free(users[arg1]);     //... but users[arg1] IS NOT reset to NULL -> UaF
```

## Solve script
Script path: `scripts/pwny.py`
Script path: `scripts/solve.py`

## Flag
sigpwny{us3_4ft3r_fre3_m0re_like_fre3_flags_for_m3}

## Lessons and reusable patterns
- Rule violated: after free(p), p = NULL. Oblivion = UaF.
- Reuse: free then malloc/calloc of the same size = we recover the same chunk (LIFO). This is what aliases two objects of different types.
- 🪤 The trap I experienced (struct offsets): logged_in is at offset 60 (after name[60]), not 64. I had put (64-len(name))*b"\0" + logged_in -> logged_in fell at offset 64 (excluding struct, truncated by the memcpy capped at 64) -> remained 0. Correct = (60-len(name))*b"\0" + p32(1). Always draw the struct and count the offsets.
- calloc resets the reused block -> logged_in starts again at 0, it MUST be rewritten.
- memcpy copies a RAW length (not strlen) into WRITE_DOC -> we can put null bytes in the middle and reach offset 60 (a strcpy would have stopped at "admin").
- strncmp(name,"admin",60): put a \0 just after "admin" (offset 5) so that the comparison matches.
