---
title: "PwnyMart"
ctf: "Pwny-CTF"
category: "pwn"
difficulty: "Not specified"
points: 250
techniques: ["format-string", "buffer-overflow", "heap-use-after-free", "stack-canary", "pie-bypass", "nx-bypass"]
tools: ["one-gadget", "netcat", "python"]
keywords: ["PwnyMart", "Pwny-CTF", "pwn", "format-string", "buffer-overflow", "heap-use-after-free", "stack-canary", "pie-bypass", "nx-bypass", "one-gadget", "netcat", "python", "libc", "canary", "pie", "got"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/PWN-I/PwnyMart/notes.md"
---

# PwnyMart (Pwny-CTF, pwn)

## Summary
Challenge **PwnyMart** from the Pwny-CTF CTF, pwn category. Main technique: format-string. The PwnyMart challenge (Pwny-CTF, pwn) is documented by a resolution note.

## Statement and artefacts
Welcome to PwnyMart, the most secure online grocery store in existence.

`nc chal.sigpwny.com 1349`

**author**: Nikhil

**Provided files / artifacts:**
- `work/README.md (text, 2.0 KB)`
- `work/challenge (file, 16.5 KB)`
- `work/challenge_patched (file, 16.5 KB)`

## Recognition signals
- Signal: Recognize: a menu that calls array[i]() + a function to modify this array = function pointer hijacking. Look for a “hidden” function (admin/win/shell) outside the menu.
- Signal: The guard!= NULL forces the sequence Remove then Add: always look at the conditions before writing, they dictate the order of moves.
- Signal: Leak offered by the program: no need for format string or overflow to beat PIE when an info/debug command already prints addresses with %p.
- Signal: scanf("%lx") expects the address in ASCII hex without 0x (the final \n is enough) — like %lu/%d expects decimal, never raw p64 bytes.
- Signal: All mitigations enabled ≠ safe binary: canary/NX/PIE/RELRO only protect against memory corruption. A logic bug (freely writing into a pointer table) completely ignores them.
- Signal: Off-by-one bonus (not used): settings tests index > OPERATIONS_SIZE (5) instead of >= -> index 5 outside the table also accessible. The clean path (index 2 in-bounds) was enough.

## Resolution method
1. **The program (challenge.c)**

- `static void (*operations[])() = {add_item, remove_item, view_cart, settings, info};` → function pointer table. `main` makes `operations[option]()` for `option` from 0 to 4.
- `admin_console()` does `execve("/bin/sh", NULL, NULL)` but **is not** in the menu (not callable normally).
- `settings()` offers two primitives on the table:
  - **Remove Operation**: `operations[index] = NULL;`
  - **Add Operation**: `scanf("%lx", &op); operations[index] = op;` → **writing an arbitrary pointer** (free hex value).
- `info()` level 1 **prints the addresses**: `operations[0..4]` **and** `admin_console` (`printf("...%p\n", admin_console)`).
- Protections: Full RELRO + Canary + NX + PIE + SHSTK + IBT → **all enabled, all useless here** (no overflow, no stack/GOT corruption).

1. Menu `4` (info) → level `1` → read the address of **`admin_console`** (ex. `0x...087f`). → PIE bypassed, we have the exact runtime address.
2. Menu `3` (settings) → `0` (Remove) → index **2** (`view_cart`) → `operations[2] = NULL`.
   - *Why Remove first:* Add refuses if `operations[index]!= NULL`. We therefore free the slot before writing.
3. Menu `3` (settings) → `1` (Add) → position **2** → value = the address of `admin_console` (without `0x`, `scanf("%lx")`). → `operations[2] = admin_console`.
4. (check) level 1 info → `Code: 2... Address: 0x...087f` = same address as admin. Confirmed.
5. Menu `2` → `main` calls `operations[2]()` = `admin_console()` → **shell** → `cat flag.txt`.

Flag: `sigpwny{fun_w17h_func710n_p01n73r5}`. Script: `work/pwny.py` (parses the leak addresses, replays the Remove/Add sequence then goes interactive).

2. **Harder variant (competitive CTF)**

- No `info` command → it would be necessary to **leak** the address differently (format string, OOB reading of the table via an out-of-bound index, leak libc + one_gadget).
- No `admin_console` function in the binary → write the address of a **one_gadget** libc (after leak of the libc base) in the slot, or chain to `system`.
- Strictly bounded index (`>=`) without Remove → look for another write primitive (OOB, UAF on the table).

3. **To remember / pitfalls**

- **Recognize**: a menu that calls `tableau[i]()` **+** a function to modify this array = function pointer hijacking. Look for a “hidden” function (admin/win/shell) outside the menu.
- **The guard `!= NULL`** forces the sequence **Remove then Add**: always look at the conditions before writing, they dictate the order of moves.
- **Leak offered by the program**: no need for format string or overflow to beat PIE when a `info`/`debug` command already prints addresses with `%p`.
- **`scanf("%lx")`** expects the address in **ASCII hex without `0x`** (the final `\n` is enough) — like `%lu`/`%d` expect decimal, never raw `p64` bytes.
- **All mitigations enabled ≠ safe binary**: canary/NX/PIE/RELRO only protect against memory corruption. A **logic bug** (freely writing to a pointer table) completely ignores them.
- **Off-by-one bonus** (not used): `settings` tests `index > OPERATIONS_SIZE` (5) instead of `>=` → index 5 outside the table also accessible. The clean path (index 2 in-bounds) was enough.

## Solve script
Script path: `scripts/pwny.py`

## Flag
sigpwny{fun_w17h_func710n_p01n73r5}

## Lessons and reusable patterns
- Main technique: format-string.
