---
title: "GOT-Overwrite"
ctf: "Pwny-CTF"
category: "pwn"
difficulty: "Not specified"
points: 500
techniques: ["format-string", "rop", "got-overwrite", "pie-bypass"]
tools: ["checksec", "one-gadget", "netcat", "python"]
keywords: ["GOT-Overwrite", "Pwny-CTF", "pwn", "format-string", "rop", "pie-bypass", "checksec", "one-gadget", "netcat", "python", "elf", "libc", "pie", "got"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Pwn/GOT-Overwrite/notes.md"
---

# GOT-Overwrite (Pwny-CTF, pwn)

## Summary
Challenge **GOT-Overwrite** from the Pwny-CTF CTF, pwn category. Main technique: format-string. The GOT-Overwrite (Pwny-CTF, pwn) challenge is documented by a resolution note.

## Statement and artefacts
Can you pwn this program and read flag.txt?

`nc chal.sigpwny.com 1379`

**author**: Nathan

**Provided files / artifacts:**
- `work/Dockerfile (file, 569 B)`
- `work/challenge (file, 16.5 KB)`
- `work/challenge_patched (file, 24.5 KB)`
- `work/ld-2.31.so (library, 187.0 KB)`
- `work/libc-2.31.so (library, 7.1 MB)`
- `work/libc.so.6 (file, 7.1 MB)`

## Recognition signals
- Signal: one_gadget: an address in the libc which, if we jump there (RIP = base + offset), launches execve("/bin/sh",.) without arguments to prepare. Found with one_gadget libc-2.31.so. Always check the constraints (required register/memory values): here the prog sets r12=r15=0, so we choose 0xe3afe whose constraints are r15==NULL && r12==NULL. A gadget with the wrong set of constraints -> crash.
- If we observe scanf("%lu") = ASCII decimal, remember to send str(n).encode(), never p64(n). (Classic error.).
- Signal: Trap sla(b"?",.) (the one that blocked me): sendlineafter waits for the pattern before sending. If we have already consumed the? of the prompt (e.g. ru(b"?") for the leak), sla(b"?",.) waits for the next prompt which only appears after our entry -> deadlock. Fix: match the entire prompt (b"Where would you like to write?") or send with a simple sl().
- Signal: Why puts@GOT: it is a function called after our single writing. No RELRO -> its GOT box is modifiable; No PIE -> its address is fixed.
- Signal: Trigger: a write-what-where is not enough, the program must re-borrow the diverted box (here puts) after writing.

## Resolution method
1. **The program (challenge.c)**

- Leak gift: `printf("libc is at %p\n",... - 0x24083)` → displays **directly the libc database**.
- Then **an arbitrary write**: reads `dest` then `value` (two `scanf("%lu")`), does `*(uint64_t*)dest = value;`.
- Put **`r12=0` and `r15=0`** just before writing → to **satisfy the constraints of a one_gadget**.
- After writing: `puts("Thanks for playing!")` → **this is the trigger**.
- `checksec`: **No PIE** (GOT fixed address) + **No RELRO** (GOT writable) + libc-2.31 provided.

1. **Leak**: read the line `libc is at 0x...` → `libc.address = <value>` (the subtraction `-0x24083` is already done by the program, so this is the basis).
2. **Target**: `dest = elf.got["puts"]` = `0x403440` (fixed because No PIE, writable because No RELRO).
3. **Value**: `value = libc.address + 0xe3afe` (one_gadget `execve("/bin/sh", r15, r12)`, constraints `r15==NULL && r12==NULL` → exactly what the prog forces).
4. Send `dest` then `value` in **ASCII decimal** (`scanf("%lu")`). The write overwrites `puts@GOT` → the `puts("Thanks…")` call jumps to the one_gadget → **shell** → `cat flag.txt`.

```python
io.recvuntil(b"libc is at ")
libc.address = int(io.recvline().strip(), 16)
dest  = elf.got["puts"]            # 0x403440
value = libc.address + 0xe3afe     # one_gadget (r15==0 && r12==0)
io.sendlineafter(b"Where would you like to write?", str(dest).encode())
io.sendlineafter(b"What would you like to write?",  str(value).encode())
io.interactive()
```
Flag: `sigpwny{you_GOT_to_find_that_one_gadget!}`.

2. **Harder variants**

- **If PIE** (binary): `puts@GOT` unknown → target a structure **in libc** (which we know via the leak): `__free_hook`/`__malloc_hook` (glibc < 2.34) + trigger a `malloc`/`free`, or divert `exit`/`_IO`.
- **If Full RELRO**: GOT read-only → no GOT overwrite; go through libc hooks or an ROP.
- **one_gadget for which no constraint is satisfied**: fall back on `system("/bin/sh")` (overwriting `puts@GOT`→`system` **does not work** directly because the argument would be “Thanks…”; rather aim for a function whose arg is controlled).

3. **To remember / pitfalls**

- **one_gadget**: an address in the libc which, if we jump there (RIP = base + offset), launches `execve("/bin/sh",...)` **without arguments to prepare**. Found with `one_gadget libc-2.31.so`. **Always check the constraints** (required register/memory values): here the program puts `r12=r15=0`, so we choose `0xe3afe` whose constraints are `r15==NULL && r12==NULL`. A gadget with the wrong set of constraints → crash.
- **`scanf("%lu")` = ASCII decimal**: send `str(n).encode()`, **never** `p64(n)`. (Classic error.)
- **`sla(b"?",...)` trap (the one that blocked me)**: `sendlineafter` **waits** for the pattern **before** sending. If we have already consumed the `?` of the prompt (e.g. `ru(b"?")` for the leak), `sla(b"?",...)` waits for the **next** prompt which only appears after our entry → **deadlock**. Fix: match the **entire prompt** (`b"Where would you like to write?"`) or send with a simple `sl()`.
- **Why `puts@GOT`**: it's a function **called after** our only writing. No RELRO → its GOT box is modifiable; PIE number → its address is fixed.
- **Trigger**: a write-what-where is not enough, the program must **re-borrow** the diverted box (here `puts`) after writing.

## Solve script
Script path: [scripts/pwny.py](scripts/pwny.py)

## Flag
sigpwny{you_GOT_to_find_that_one_gadget!}

## Lessons and reusable patterns
- Main technique: format-string.
