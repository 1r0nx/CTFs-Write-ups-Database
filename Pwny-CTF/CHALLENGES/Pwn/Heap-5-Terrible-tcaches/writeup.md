---
title: "Heap-5-Terrible-tcaches"
ctf: "Pwny-CTF"
category: "pwn"
difficulty: "Not specified"
points: 600
techniques: ["format-string", "heap-use-after-free", "double-free", "tcache-poisoning", "pie-bypass", "reverse-engineering", "git-forensics", "malware-analysis"]
tools: ["pwntools", "objdump", "checksec", "netcat", "python"]
keywords: ["Heap-5-Terrible-tcaches", "Pwny-CTF", "pwn", "format-string", "heap-use-after-free", "double-free", "tcache-poisoning", "pie-bypass", "reverse-engineering", "git-forensics", "malware-analysis", "pwntools", "objdump", "checksec", "netcat", "python"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Pwn/Heap-5-Terrible-tcaches/notes.md"
---

# Heap-5-Terrible-tcaches (Pwny-CTF, pwn)

## Summary
Challenge **Heap-5-Terrible-tcaches** from the Pwny-CTF CTF, pwn category. Main technique: format-string. Internal allocator to get a malloc at an arbitrary address, and use it to overwrite the GOT of exit by system.

## Statement and artefacts
Changelog:
 - Removed the login feature
 - Removed `documents` (apparently they were introducing security problems)
 - Users can have the same name as other users
 - `del_user` can delete the currently selected user, too

Oh yeah, we also removed that `admin` testing feature we accidentally left in.

(This challenge is hard and will require pwntools as well as downloading the binary and inspecting the addresses. Note that ASLR is off & relro is set to partial- that means the GOT is always in the same place, and is always writeable!)

`nc chal.sigpwny.com 1364`

Two binary gifts (visible via `checksec` + the source code):

1. **Partial RELRO + No PIE** → the **GOT** (the array of pointers to libc functions) is **writable** *and* at a **fixed address**. `objdump -D heap5 | grep exit@` gives: `exit@GLIBC` → **`0x404070`** (confirmed by the free index).
2. In `handle_choice`, the command `exit` literally does:
   ```c
   case EXIT:
       exit((int64_t)"/bin/sh");   // rdi = pointer to the string "/bin/sh"
   ```
So `exit` is called **with `"/bin/sh"` as first argument** (register `rdi`).

**Consequence**: if we replace `exit@GOT` (0x404070) with the address of `system`, then typing `exit` does not exit — it executes `system("/bin/sh")` → **shell**. And since `leak_system` prints us `&system` (`printf("%p", &system)`), we don't even need to calculate a libc offset**.

---

**Provided files / artifacts:**
- `work/heap5 (file, 23.0 KB)`
- `work/heap5_patched (file, 31.0 KB)`
- `work/ld-2.31.so (library, 187.0 KB)`
- `work/libc-2.31.so (library, 7.1 MB)`
- `work/libc.so.6 (file, 7.1 MB)`

## Recognition signals
- If we observe “del_user can delete the currently selected user, too”, think of del_user done.
- If we observe rename_user does memcpy(current_user, arg1, arg1_len), think of a controlled size write.
- Signal: Payload of rename_user WITHOUT \nfinal.
- Signal: The parser calculates arg1_len = bytes_read - 12 (12 = "rename_user").
- Signal: If we sent sendline (add \n), this \n would count in the length and would be copied by memcpy -> it would corrupt the byte just after the target (ex.
- Signal: 0x404078, the neighboring GOT input).

## Resolution method
1. **Reminders to understand the rest**

If these foundations are already solid, jump to §3.

- **Heap** = the memory that `malloc(n)` distributes, and that `free(p)` returns to the allocator (glibc). Each rendered block is a **chunk**: 16 header bytes (`prev_size`, `size`) followed by the data being manipulated. `malloc(128)` gives a chunk of size **0x90** (128 data + header, rounded to the multiple of 16).
- **tcache** (glibc ≥ 2.26) = a small cache **by size**, specific to the thread. When you `free` a chunk, it is placed **at the top** of a simply linked list (the “bin” of its size), up to 7. The next `malloc` of this size **brings out this chunk first** (LIFO, like a stack of plates).
- **How ​​is the list linked?** Glibc reuses **the first 8 bytes of the released chunk data** to store the pointer to the next chunk in the bin: this is the `fd` (or `next`) field. In other words, *in a free chunk*, the data that we saw before is overwritten by this pointer.

      Free chunk in cache (glibc 2.31):
      +------------------+
      | header (size…)   |
      +------------------+  <- what malloc returns (start of "data")
      | fd = next chunk  |  <- 8 bytes: next chunk in the bin (0 if last)
      | key = &tcache    |  <- 8 bytes: anti double-free
      |      ...         |
      +------------------+

- **The idea of *poisoning***: if we manage to **write ourselves in this `fd`**, we lie to the allocator about “the address of the next free chunk”. It will end up **serving this address** for us like a normal chunk → we write wherever we want. That's the whole attack.

---

2. **Why glibc 2.31 is the key (safe-linking)**

- From **glibc 2.32**, `fd` is no longer stored in plain text: it is hidden by `fd ^ (chunk_address >> 12)` (*safe-linking*). Forging a valid `fd` would then require **knowing the address of the heap** (thus a prior leak).
- Here it is **2.31** (`info` the announcement, and `./libc-2.31.so`). So **no safe-linking**: the `fd` is a **raw pointer**. You can write the address you want there **without any leak from the heap**. This is what makes this challenge “simply” doable. Always check the libc version first.

---

3. **Exploit progress (with the status of the cache at each step)**

Starting state: `users[0]` = "admin" (created by `main`), `current_user = users[0]`. Affected tray = `tcache[0x90]` (all users are 0x90).

**a) Create two chunks to poison**
```
create_user   -> users[1] = C1
create_user   -> users[2] = C2
```

**b) Free them, C2 released LAST while remaining `current_user`**
```
del_user 1        free(C1)            tcache[0x90]:  C1            (count=1)
switch_user 2     current_user = C2
del_user 2        free(C2)  (UAF!)    tcache[0x90]:  C2 -> C1      (count=2)
```
> **Why two `free` and not just one?** In glibc 2.31, `malloc` is only used from the task if `counts[idx] > 0`. If we had only released one chunk (count=1), the **first** `malloc` released it (count→0) and the **second** `malloc` would find the “empty” bin → it would look elsewhere and never give us back the forged address. With **count=2**, after the 1st `malloc` there remains count=1: the 2nd `malloc` follows the `fd` that we tampered with. **Rule: count ≥ 2.**

**c) Poison C2's `fd` (the freed chunk = `current_user`)**
```
rename_user <8 bytes = p64(0x404070)> memcpy(C2, &0x404070, 8)
                                            tcache[0x90]:  C2 -> 0x404070   (count=2)
```
> We have just written, in the `fd` of C2, the address of `exit@GOT`. The allocator now believes that "the free chunk after C2" is at **0x404070**.

**d) Two allocations: the 2nd gives us the GOT**
```
create_user   -> malloc(0x90) ressort C2        users[3] = C2        (count=1)
create_user   -> malloc(0x90) ressort 0x404070  users[4] = 0x404070  (count=0)
```
> The output displays `Created user 4 at 0x404070`: the allocator did indeed give us the GOT as if it were a chunk. (2.31 doesn't check alignment in cache; 0x404070 is 16-aligned, so it works fine.)

**e) Write `system` in the GOT via this "user"**
```
switch_user 4                         current_user = 0x404070
rename_user <8 bytes = p64(&system)> memcpy(0x404070, &system, 8)
                                      => exit@GOT = system
```

**f) Trigger**
```
exit -> exit("/bin/sh") -> (hijacked GOT) -> system("/bin/sh") -> SHELL
```
Then `cat flag*` returns the flag (`uid=1000(pwn)` on the remote side).

---

4. **The flaw in the code (where do we write the fd?)**

You need a **write primitive in a freed chunk**. The changelog blows it away:

- **“`del_user` can delete the currently selected user, too”**: `del_user` does `free(users[arg1]); users[arg1]=NULL;` **but does not touch `current_user`**. So if we delete the currently selected user, `current_user` continues to point to a chunk **freed**: it is a **ghost pointer** (*dangling*) → **Use-After-Free**.
- `rename_user` does `memcpy(current_user, arg1, arg1_len)`: a **size-controlled write** in the chunk pointed to by `current_user`. Applied to a freed chunk, it writes **stack on its `fd`** (the first 8 bytes).

→ We hold everything: UAF to have a freed chunk **always accessible** for writing, and `rename_user` to put the `fd` we want there.

---

5. **The two pwntools pitfalls (important)**

1. **Payload of `rename_user` WITHOUT final `\n`.** The parser calculates `arg1_len = bytes_read - 12` (12 = `"rename_user "`). If we sent `sendline` (add `\n`), this `\n` would count in the length and would be **copied by `memcpy`** → it would corrupt the **byte just after** the target (e.g. `0x404078`, the neighboring GOT entry). Hence the use of `sendafter` / `send` (raw bytes, without newline). The null bytes of the address (`0x404070` = `70 40 40 00 00 00 00 00`) are not a problem: `read()` reads raw bytes and `memcpy` copies by **length**, not up to `\0`.

2. **Do not paste the shell command behind `exit` in the same burst.** The menu reads with `read(0, buf, 128)`, which swallows **everything available at once**. If `exit\n` and `id\n` arrive stuck, the `read` from the menu *also* consumes the `id\n` (lost), then `exit`→`system` launches a shell whose stdin is **already empty** → it closes without executing anything. **Observed symptom**: the leak works, the GOT is overwritten (the prompt displays the bytes of `system`), but the shell "does not respond". **Parade**: `sendlineafter("> ", "exit")` then `sleep(1.5)` **before** writing the first command in the shell.

---

6. **To remember — how to recognize this type of challenge**

- *heap* type menu (create / delete / edit objects) **+** glibc **≤ 2.31** (no safe-linking) **+** Writable GOT (**Partial RELRO + No PIE**) **+** a primitive for **writing in a freed chunk** → think **tache poisoning towards the GOT**.
- The `exit((int64_t)"/bin/sh")` wired into the code is the **ready-made detonator**: aiming for `exit@GOT` avoids having to find a gadget or deal with arguments (rdi is already `"/bin/sh"`).
- Recon reflexes which decided everything: `checksec` (RELRO/PIE), `objdump … | grep exit@` (GOT address), read the **changelog** of the description (it points out the flaw: *free from the current user*), identify the **libc version** (safe-linking or not).
- **ASLR**: announced *off* on the remote side, but **useless** here — the GOT is fixed (No PIE) and `system` is leaked. The exploit works **even ASLR enabled** (checked locally, ASLR on).
- **Harder variant (competitive CTF)**: glibc **≥ 2.32** → safe-linking ⇒ it would first be necessary to leak the heap** to forge `fd = target ^ (chunk >> 12)`. Full RELRO ⇒ GOT read-only ⇒ aim instead for `__free_hook` / `__malloc_hook` (≤ 2.33) or the *exit handler* `_IO`/`__run_exit_handlers`. No `leak_system` offered ⇒ leak the libc via an *unsorted bin* chunk (address `main_arena`).

## Solve script
Script path: [scripts/pwny.py](scripts/pwny.py)
Script path: [scripts/solve.py](scripts/solve.py)

## Flag
sigpwny{ar3n't_tcach3s_just_y0ur_fav0r1t3_th1ng5????}

## Lessons and reusable patterns
- Main technique: format-string.
