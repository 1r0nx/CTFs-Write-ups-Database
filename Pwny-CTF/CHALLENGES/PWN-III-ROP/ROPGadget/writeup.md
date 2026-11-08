---
title: "ROPGadget"
ctf: "Pwny-CTF"
category: "pwn"
difficulty: "Not specified"
points: 300
techniques: ["xor-cipher", "rop", "stack-canary", "pie-bypass", "nx-bypass"]
tools: ["pwntools", "checksec", "ropgadget", "netcat", "python"]
keywords: ["ROPGadget", "Pwny-CTF", "pwn", "xor-cipher", "rop", "stack-canary", "pie-bypass", "nx-bypass", "pwntools", "checksec", "netcat", "python", "https", "xor", "canary"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/PWN-III-ROP/ROPGadget/notes.md"
---

# ROPGadget (Pwny-CTF, pwn)

## Summary
Challenge **ROPGadget** from the Pwny-CTF CTF, pwn category. Main technique: xor-cipher. Write "/bin/sh" to memory (.data) then execute via syscall. No win, no /bin/sh provided.

## Statement and artefacts
`nc chal.sigpwny.com 1370`

Can you pwn this binary and read flag.txt? This binary has some helpful gadgets already in it for you to use.

Use [ROPgadget](https://github.com/JonathanSalwan/ROPgadget) to automatically generate a ropchain (see slides) and send that payload to the netcat using pwntools!

- `main`: `char answer[32]` + **`gets(answer)`** → unlimited BOF. No `win`.
- Protections: **No PIE** (fixed addresses), **No canary**, **NX**, **Partial RELRO** (→ `.data` **writable**).
- No `"/bin/sh"` in the binary → you have to **write it yourself**.

**Provided files / artifacts:**
- `work/chal (file, 15.9 KB)`
- `work/chal_patched (file, 15.9 KB)`

## Recognition signals
- Signal: write "/bin/sh" to memory (.data) then execute via syscall. No win, no /bin/sh provided.

## Resolution method
1. **Recon** — `checksec` (No PIE/No canary/NX), source: `gets` = BOF, no win or /bin/sh.
2. **Offset** — `cyclic` → **40** (`answer[32]` + 8 saved RBP). ⚠️ different from ROP 1-3 (56): the frame depends on the binary.
3. **Generate the string** with the eponymous tool:

```bash
   ROPgadget --binary chal_patched --ropchain
   ```

1. It produces a string that:
   - written `"/bin//sh"` (8 B) in `.data`: `pop rax=.data`; `pop rbx="/bin//sh"`; `mov [rax], rbx`.
   - writes `0` to `.data+8`: `pop rax=.data+8`; `xor rbx, rbx`; `mov [rax], rbx`.
   - args execve: `pop rdi=.data`; `pop rsi=.data+8` (+`pop r15` junk); `pop rdx=.data+8`.
   - `rax=59`: `xor rax, rax` then **`inc rax` ×59** (tool signature, no `pop rax=59`).
   - `syscall` → `execve("/bin//sh", {NULL}, {NULL})`.
4. **Payload**: `b'A'*40 + <ropchain>`, sent with `sla(b"name?", p)` → shell → `cat flag.txt`.

## Solve script
Script path: `scripts/pwny.py`

## Flag
sigpwny{getting_the_hang_of_rop}

## Lessons and reusable patterns
- Recognize: “ROPGadget”, no win or /bin/sh, No PIE -> let the tool generate ROPgadget --ropchain. Great for understanding the anatomy of an execve chain.
- Write-what-where primitive in ROP: pop rax(address) + pop rbx(8 bytes) + mov [rax], rbx = write a qword to an address. Used to set "/bin/sh" to.data/.bss (writable because NX ≠ writing, and Partial RELRO leaves.data writable).
- "/bin//sh" = exactly 8 bytes (fits in a qword); the double / is ignored by the kernel.
- inc rax ×59: build a syscall number without a gadget pop rax=<n> — verbose but robust.
- Same execve as ROP 2 - Silly Syscalls, but here /bin/sh is NOT provided -> we write it, and it is the TOOL that puts everything together.
