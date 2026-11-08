---
title: "Heap-3-Double-Free"
ctf: "Pwny-CTF"
category: "pwn"
difficulty: "medium"
points: 500
techniques: ["heap-use-after-free", "double-free", "tcache-poisoning"]
tools: ["netcat", "python"]
keywords: ["Heap-3-Double-Free", "Pwny-CTF", "pwn", "heap-use-after-free", "double-free", "tcache-poisoning", "netcat", "python", "libc", "uaf", "tcache", "heap"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Pwn/Heap-3-Double-Free/notes.md"
---

# Heap-3-Double-Free (Pwny-CTF, pwn)

## Summary
Challenge **Heap-3-Double-Free** from the Pwny-CTF CTF, pwn category. Main technique: heap-use-after-free. A challenge name is a clue: “Double Free” announced the technique. Here the solution from the previous episode was already the expected solution.

## Statement and artefacts
We finally fixed that nasty use after free bug. While we were at it, we made a few changes to the code. Now, the selected user object is tracked with a pointer to where that user was allocated, instead of by its user ID. (We figured one less level of indirection should make things quicker, right?)

Due to popular demand, we've also added the ability to delete the currently selected user. How convenient, right?

Don't forget, our app disables the `tcache` so that all allocation happens in `fastbins`.

This challenge is nearly identical to `heap2` except it is hardened against the extra UaF that Justin found. Your solution should require a double free.

`nc chal.sigpwny.com 1362`

**Provided files / artifacts:**
- `work/heap3 (file, 32.5 KB)`
- `work/heap3_patched (file, 40.0 KB)`
- `work/ld-2.31.so (library, 187.0 KB)`
- `work/libc-2.31.so (library, 7.1 MB)`
- `work/libc.so.6 (file, 7.1 MB)`

## Recognition signals
- Signal: A challenge name is a clue: “Double Free” announced the technique. Here the solution from the previous episode was already the expected solution.
- Signal: A protection is only valid if it is executed at the right time on the right object: document cleanups[] only run in the del, never afterwards, and on the wrong table for us.

## Resolution method
1. **The observation**

Solved with Heap-2 script **without any modifications** (just `--port 1362`). Flag: `sigpwny{i_th1nk_th1s_is_finally_d0ubl3_tr0ubl3_d0ubl3_tr0ubl3}`.

To understand why, we compare the two sources (`diff challenge.c`) instead of assuming.

---

2. **What HAS NOT changed (the heart)**

- **Identical structures**: `user_t{char name[60]; uint32_t logged_in;}` = 64 B, `document_t{char text[64];}` = 64 B → same size class.
- **Allocator** (`create_user`) and **`fill_tcaches()`** identical (checked by diff). So the 0x50 task is full at startup + `calloc` skips the task ⇒ **everything is done in fastbin**, exactly like Heap-2.
- **The final check `shell` is word for word the same**:
```c
if (!strncmp(current_user->name, "admin", NAME_LEN)) {   // test 1: the name
    if (!is_user_in_table(current_user)) {               // test 2: pointer in users[]
        printf("Currently selected user isn't in the table...");
        return;
    }
    system("/bin/sh");
}
```
- Author's comment just above (which says it all):
```c
// Prevent user from simply deleting selected, creating a new doc, and yeeting to admin
// Want to force them to actually cause a double free!
```
→ Heap-3 **wants** the double free technique. This is the intended canonical solution, not a workaround. The Heap-2 script IS the correct answer to Heap-3.

---

3. **What Heap-3 ADDS (and why it's inert on us)**

The diff does not take away anything, it adds 3 defensive safeguards:
1. **`del_user`**: after `free`, scans `documents[]` and sets to NULL any entry pointing to the deleted user.
2. **`del_selected`**: the same if `current_user` appeared in `documents[]`.
3. **`SHOW_USERS`**: displays `current_user` + warns if it is not in the table (cosmetic).

Purpose of (1) and (2): break the **aliasing user↔document** after a deletion.

Why this doesn't affect our channel:
```
create_user u2/u3/u4 ; switch_user 2
del_user 3 ; del_selected ; del_user 4 ; del_selected   <- phase double free
create_user u5 ; create_user u6 ; create_doc ; write_doc 0 "admin"+p32(1) ; shell
```
- **During the 4 `del`**: no document yet exists (`documents[]` all NULL) → the `for j … documents[j]==…` loops never match. Zero effect.
- **After aliasing established**: no more `del` is played → the cleanup loops never return to the trapped chunk.
- Above all: the aliasing that counts for **test 2** is **user↔user** (`current_user == users[i] == C`, two *user* pointers on the same chunk). `documents[0]` which also points to `C` is just a way to write "admin" into it, and `is_user_in_table` ONLY looks at the users table. The added protections targeted a variant (user↔document) that our solution does not take.

---

4. **Reminder of the technique (see Heap-2 for details)**

Double free in fastbin (`free(A);free(B);free(A)` with a free interspersed to avoid `fasttop`) → a single chunk `C` leaves allocation twice → it is both in `users[]` (test 2 OK) AND pointed by `current_user` never reassigned (test 1: name="admin"). LIFO reoccupancy order: `C` returns to the table first, then the "trash", then `create_doc`+write last to place "admin".

---

## Solve script
Script path: `scripts/pwny.py`

## Flag
sigpwny{i_th1nk_th1s_is_finally_d0ubl3_tr0ubl3_d0ubl3_tr0ubl3}

## Lessons and reusable patterns
- A challenge name is a clue: “Double Free” announced the technique. Here the solution from the previous episode was already the expected solution.
- Always diff the source between two episodes of a series rather than assuming: we see that Heap-3 only adds protections, and that they are out of our way.
- Protection is only valuable if it is executed at the right time on the right object: document cleanups[] only run in the del, never afterwards, and on the wrong table for us.
- Serial progression: Heap-0 (freed guard logged_in) -> Heap-1 (logged_in=0 before free) -> Heap-2 (is_user_in_table -> double free obligatory) -> Heap-3 (same rules + inert user↔document guardrails: Heap-2 exploit replayed as is).
