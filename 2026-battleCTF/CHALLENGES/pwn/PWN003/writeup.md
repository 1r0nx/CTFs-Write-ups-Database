---
title: "PWN003"
ctf: "2026-battleCTF"
category: "pwn"
difficulty: "Not specified"
points: 68
techniques: ["xor-cipher", "format-string", "heap-use-after-free", "stack-canary", "pie-bypass", "nx-bypass"]
tools: ["python"]
keywords: ["PWN003", "battleCTF", "pwn", "xor-cipher", "format-string", "heap-use-after-free", "stack-canary", "pie-bypass", "nx-bypass", "python", "xor", "libc", "canary", "pie", "got", "uaf"]
status: "solved"
has_script: true
source: "battleCTF/CHALLENGES/pwn/PWN003/notes.md"
---

# PWN003 (battleCTF, pwn)

## Summary
Challenge **PWN003** from the battleCTF CTF, pwn category. Main technique: xor-cipher. Challenge PWN003 (battleCTF, pwn) is documented by a resolution note.

## Statement and artefacts
Get a shell on the remote host and read the flag.

**Provided files / artifacts:**
- `work/notes (file, 16.7 KB)`

## Recognition signals
- Signal: Note menu (Add/Free/Edit/View/Exit). Alloc custom palloc/pfree (classes 0x20/0x40/0x80) + malloc/free fallback for >0x80.
- Signal: 2 globals: notes[8] (pointers) and notes_storage[8] (structs 0x18). Struct = {formatter(ptr function), content(ptr), size}.
- If we observe view_note does formatter(content), think of function pointer call.
- If we observe default_formatter(buf) = write(1, buf, 0x20), think about dumping 32 raw bytes (perfect for leaks, no \0/\n truncation).
- Signal: Free PIE leak: main displays [debug] build id: %p = &main -> base = leak − 0x1af8.
- If we observe UAF: free_note releases the content but does not put notes[idx]=NULL, think about view/edit/free still possible after free.

## Resolution method
1. **Method (full string)**

1. PIE leak (banner).
2. `add(0)`, `add(1)` (class 0). `free(1)` → `*X = rol(X,13)`. `view(1)` (UAF) → dump → `ror13` → **pool address `X`**.
3. **Poisoning**: `edit(1)` writes `*X = notes_storage ^ rol(X,13)`. `add(4)` (pop
4. Edit ctrl = **rewrite `notes_storage[0]`** (the meta of note 0). We put `formatter=default_formatter, content=&got[x]` then `view(0)` → libc leak (puts/read/printf). Libc identity via **libc.rip** (3 symbols to remove ambiguity).
5. `edit(ctrl)` → `notes_storage[0] = {system, &"/bin/sh", 0}`; `view(0)` → **`system("/bin/sh")`**. Flag in `/flag/flag.txt`.

2. **Recognition**

- Notes menu (Add/Free/Edit/View/Exit). Custom allocation `palloc/pfree` (classes 0x20/0x40/0x80) + fallback `malloc/free` for >0x80.
- 2 globals: `notes[8]` (pointers) and `notes_storage[8]` (structs 0x18). Struct = `{formatter(function ptr), content(ptr), size}`.
- `view_note` does **`formatter(content)`** → function pointer call.
- `default_formatter(buf)` = `write(1, buf, 0x20)`: **dump 32 raw bytes** (perfect for leaks, no `\0`/`\n` truncation).

3. **Flaws**

1. **Free PIE leak**: `main` displays `[debug] build id: %p` = `&main` → base = leak − 0x1af8.
2. **UAF**: `free_note` releases the content but **does not release `notes[idx]=NULL`** → view/edit/free still possible after free.
3. **Safe-linking breakable**: freelist stores `next ^ rol(chunk,13)`. `palloc` pop **without terminal control** → we can return an arbitrary address.

4. **To remember / pitfalls**

- **Recognize**: notes menu + `free` which does not NULL the pointer = UAF; custom allocator with XOR/rot = safe-linking → poisoning if no bound.
- **Leak**: prefer `default_formatter` (`write` fixed size) to `puts` — a libc address containing `0x0a` truncates `recvline` (bug encountered here on `puts`).
- **Libc unknown**: leaker **multiple** symbols (puts+read+printf) for a single match on libc.rip; check consistency (base since puts should predict read/printf). Here: `libc6_2.42-13_amd64`.
- `call rdx` in normal function = stack already well aligned → `system` does not crash (no need for `ret` alignment).
- Script: `work/solve.py` (`--remote` for target).

## Solve script
Script path: `scripts/solve.py`

## Flag
CTF{0b1578aa1b39f4c6ab9a857a657ee71aKABO....!}

## Lessons and reusable patterns
- Main technique: xor-cipher.
