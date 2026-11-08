---
title: "Heap-4-Heap-Overflow"
ctf: "Pwny-CTF"
category: "pwn"
difficulty: "Not specified"
points: 550
techniques: ["buffer-overflow", "double-free", "heap-overflow", "tcache-poisoning"]
tools: ["gdb", "netcat", "gcc", "python"]
keywords: ["Heap-4-Heap-Overflow", "Pwny-CTF", "pwn", "buffer-overflow", "double-free", "heap-overflow", "tcache-poisoning", "gdb", "netcat", "gcc", "python", "libc", "tcache", "heap"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Pwn/Heap-4-Heap-Overflow/notes.md"
---

# Heap-4-Heap-Overflow (Pwny-CTF, pwn)

## Summary
Challenge **Heap-4-Heap-Overflow** from the Pwny-CTF CTF, pwn category. Main technique: buffer-overflow. Name = hint: "Heap Overflow" -> overflow. A memcpy with a capped length > buffer size = overflow by construction (here the comment // Artificial 10 byte overwrite).

## Statement and artefacts
The `del_selected` feature was incredibly unpopular and introduced some security problems, so we removed it for this version. We also are thinking of making this program multithreaded, so we finally enabled the `tcache`.

We also made `document_t`'s bigger so they fit into their own allocation group. This way `user_t` and `document_t` objects never get allocated to the same heap chunks. Finally, we changed the way that `write_doc` works.

You know, maybe we ought to triple check there's no buffer overflows introduced in this version...

`nc chal.sigpwny.com 1363`

**Provided files / artifacts:**
- `work/heap4 (file, 32.1 KB)`
- `work/heap4_patched (file, 40.0 KB)`
- `work/ld-2.31.so (library, 187.0 KB)`
- `work/libc-2.31.so (library, 7.1 MB)`
- `work/libc.so.6 (file, 7.1 MB)`

## Recognition signals
- If we observe bytes 0.79, think of text[80] (legitimate).
- If we observe bytes 80.87, think of prev_size of the next chunk (inert in cache, simple padding).
- If we look at byte 88 (0x58), think of the low byte of the size of the next chunk ← the real target.
- If we observe byte 89, think about forcing 0x00 by the code (doc_contents[89]='\0').
- Signal: b heap4.c:446 never triggers: gcc splits the memcpy line into “discriminators”, and gdb sets the breakpoint at an off-path address (0x1d6e) while the memcpy call is at 0x1cb0. Fix: break on the real address -> b handle_choice+0x59e (just after the memcpy call). General reflex: disassemble <fn>, locate call …<memcpy@plt>, b <next instruction>.
- Signal: Read input: read(0, userbuf, 128) reads a burst and keeps only one line; sending pasted commands (file) desynchronizes everything (Invalid command! in a loop). sendlineafter(prompt) remains in sync because it waits for the prompt.

## Resolution method
1. **What changes vs Heap 2/3 (diff source)**

- `fill_tcaches()` **commented** → we play in **tcache** (no longer in fastbin). Empty bins at departure.
- **Different** sizes: `user_t{char name[60]; uint32_t logged_in}` = chunk **0x50** (80); `document_t{char text[80]}` = chunk **0x60** (96). `assert(sizeof(user_t)!= sizeof(document_t))`. Separate bins → direct user↔doc aliasing from previous episodes is **dead**.
- `malloc` instead of `calloc` → chunks reused **not reset**.
- More `del_selected`; `del_user` remains (releases a user 0x50). **No deletion or `del_doc`** (but `show_docs` exists = read/leak possible).

2. **Method (solve it, work/pwny.py)**

```python
sla(b">", b"create_user u2")                        # layout
sla(b">", b"create_doc")                            # D = documents[0] (BEFORE the victim)
sla(b">", b"create_user u3")                        # users[3] = VICTIM (corrupted then released)
sla(b">", b"create_user u4")                        # users[4] = TARGET (remains in table -> "admin")
sla(b">", b"write_doc 0 " + cyclic(88) + b"\x61")   # overflow D: size of u3 0x51 -> 0x61
sla(b">", b"del_user 3")                            # free(u3) read size=0x61 -> u3 in tcache[0x60]
sla(b">", b"create_doc")                            # D2 = documents[1]: takes the chunk of u3 -> covers u4
sla(b">", b"write_doc 1 " + cyclic(80) + b"admin")  # overflow D2: "admin" STACK on name[0..4] of u4
sla(b">", b"switch_user 4")                         # current_user = u4: "admin", logged_in=1, in table
sla(b">", b"shell")                                 # strncmp OK + in_table OK -> system("/bin/sh")
```
Why it works, step by step:
1. **D before u3** + **u3/u4 created before the overflow**: the corruption of the `size` of u3 **holds** (otherwise a later `malloc` rewrites a new `size` — see trap).
2. `size` 0x51→0x61: at `del_user 3`, `free` indexes the bin according to `size` → u3 (physically 0x50) leaves in **`tcache[0x60]`**. (Tcache 2.31 does not check size consistency; it only needs the `size` and the anti-double-free key.)
3. `create_doc`: `malloc(0x60)` springs u3 from `tcache[0x60]` (LIFO). D2 lands **on the old location of u3**. Since D2 did 0x60 and u3 did 0x50, D2 **overflows 0x10 (16) onto u4** (next chunk). → **superimposed chunks**.
4. In D2: `name[0]` of u4 falls exactly at **byte 80** of the write (start of the overflow zone). `cyclic(80)+"admin"` (85 bytes, no ceiling) therefore places `"admin"` on `u4->name[0..4]`. `u4->name[5]` remains `0` (original name) → `strncmp(...,"admin",60)` match. `u4->logged_in` (out of range) remains **1**, u4 **never released** → `is_user_in_table` OK.
5. `switch_user 4` (u4 logged_in) then `shell` → shell.

3. **The fault (source)**

`write_doc` (case `WRITE_DOC`): `memcpy(documents[arg1]->text, doc_contents, arg1_len)` with `arg1_len` capped at `DOCUMENT_LEN + 10 = 90`, while `text` is 80. **10 bytes of overflow.** Write mapping (data at `chunk+0x10`):
- bytes 0..79 → `text[80]` (legitimate)
- bytes 80..87 → `prev_size` of the chunk **next** (cached inert, simple padding)
- byte **88** (0x58) → **low byte of `size` of the next chunk** ← the real target
- byte 89 → forced to `0x00` by code (`doc_contents[89]='\0'`)

The `shell` check (unchanged since Heap 2): `strncmp(current_user->name,"admin",60)==0` **AND** `is_user_in_table(current_user)`. Purpose = `current_user` = a user **in `users[]`**, `logged_in!=0`, **named "admin"**.

4. **GDB pitfalls encountered (debug)**

- **`b heap4.c:446` never triggers**: gcc splits the `memcpy` line into “discriminators”, and gdb sets the breakpoint at an **off-path** address (0x1d6e) while the `call memcpy` is at 0x1cb0. **Fix**: break on the real address → `b *handle_choice+0x59e` (just after `call memcpy`). General reflex: `disassemble <fn>`, spot `call …<memcpy@plt>`, `b *<next instruction>`.
- **Read input**: `read(0, userbuf, 128)` reads **a burst** and keeps only one line; sending pasted commands (file) desynchronizes everything (`Invalid command!` in a loop). `sendlineafter(prompt)` remains in sync because it waits for the prompt.
- **See the heap**: `vis`/`vis_heap_chunks` (content + chunks), `tcachebins` (contents of the cache bins, the clearest to see a hole / a misplaced chunk). A free tcache 2.31 chunk = `fd` (chaining) then `key` (pointer to the tcache struct, anti-double-free).

## Solve script
Script path: `scripts/heap4.c`
Script path: `scripts/pwny.py`

## Flag
sigpwny{tls_is_wh3re_i_h1de_my_deepest_s3cret5}

## Lessons and reusable patterns
- Name = hint: "Heap Overflow" -> overflow. A memcpy with a capped length > buffer size = overflow by construction (here the comment // Artificial 10 byte overwrite).
- The overflow only reaches the size of the neighbor (byte 88). You cannot write a deep logged_in directly -> you have to superimpose a document on a user to write his name.
- Manipulate the cache size: the free/malloc bin is chosen based on the size field. Lying about the size (0x51->0x61) puts a chunk 0x50 in the bin 0x60 -> a create_doc takes it back -> recovery. We can ONLY allocate 0x50 (create_user) and 0x60 (create_doc): the only useful falsified size is 0x61.
- Allocation order = all: the victim must exist before the overflow (otherwise malloc rewrites its size), and the target must be created after the victim (to be the chunk covered by D2).
- No need to leak libc: system("/bin/sh") is already wired in shell; the work is 100% on the heap data.
- prev_size inert here: cache does not consolidate and we cannot free a document -> the prev_size/backward consolidation track does not apply. The lever is size.
