---
title: "printf-write"
ctf: "Pwny-CTF"
category: "pwn"
difficulty: "Not specified"
points: 500
techniques: ["format-string", "got-overwrite", "stack-canary", "pie-bypass", "nx-bypass"]
tools: ["pwntools", "gdb", "checksec", "netcat", "docker", "python"]
keywords: ["printf-write", "Pwny-CTF", "pwn", "format-string", "got-overwrite", "stack-canary", "pie-bypass", "nx-bypass", "pwntools", "gdb", "checksec", "netcat", "docker", "python", "elf", "libc"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/PWN-II/printf-write/notes.md"
---

# printf-write (Pwny-CTF, pwn)

## Summary
Challenge **printf-write** from the Pwny-CTF CTF, pwn category. Main technique: format-string. The printf-write (Pwny-CTF, pwn) challenge is documented by a resolution note.

## Statement and artefacts
Can you execute the `win` function?

NOTE: This challenge difficulty is now similar to 'grander finale' due to Ubuntu changes.

`nc chal.sigpwny.com 1372`

**Author**: Nathan

**Provided files / artifacts:**
- `work/Dockerfile (file, 394 B)`
- `work/challenge (file, 16.2 KB)`
- `work/challenge_patched (file, 16.9 KB)`

## Recognition signals
- Signal: elf.sym vs elf.got (error #1): to jump to YOUR function (win) -> elf.sym (code address). To divert the call of a libc function -> elf.got (writable case). Here sym["__stack_chk_fail"]=0x10f4 (PLT, read-only) ≠ got["__stack_chk_fail"]=0x3478 (GOT). Aim for the PLT = write which fails, nothing diverted.
- Signal: Stack offsets = specific to the environment: the main leak is %523$p in local-direct but %525$p in remote/docker; similarly canary_addr = rsi-0x10f8 (local) vs rsi+0x36A8 (remote). Reason: what is stacked above main (env, argv, loader, libc) shifts the stack -> delta leak->target changes. Measure in an environment that replicates remote: deploy Dockerfile with gdb added, attach, read true distance. An offset measured locally "works for you" but not on the server.
- Signal: Canary bypassed without the leaker: we do not read the canary, we set it to 0 and we turn its corruption to our advantage (the check becomes the win trigger). Variant of the “hijack rather than hijack” idea.
- Signal: [!] padding is negative, this will not work on glibc = warning pwntools benin (order of %n); it even appears when the exploit succeeds.
- Signal: buf = 0x1000 bytes = 512 slots of 8 B -> hence very large %N$p offsets (~523/525) to exceed the buffer and reach the saved RIP.

## Resolution method
1. **The program (challenge.c)**

- `main()`: `char buf[0x1000];`, twice `fgets(buf, 0x1000, stdin)` then `printf(buf)` → **two format string bugs**.
- `win()`: `puts(read_flag())` (never called).
- `checksec`: **No RELRO** (Writable GOT), **Canary**, NX, **PIE**. No RELRO + PIE + canary = you must leak the base AND bypass the canary.

2. **Strategy (write-what-where via %n)**

We cannot overwrite the saved RIP properly (canary in the middle). Tip: **hijack `__stack_chk_fail`**.
1. **1st FSB (prompt "friend?")** = leaks:
   - `%525$p` → address of **`main`** (back on the stack) → `base = main_leak - elf.sym["main"]`, `elf.address = base`.
   - `%1$p` → **RSI** (a stack address) → is used to locate the canary.
2. Calculation of targets:
   - `win = elf.sym["win"]` (we **jump** to our function → `sym`, not `got`).
   - `target = elf.got["__stack_chk_fail"]` (we **hijack** a libc function → **`got`**, the writable entry).
   - `canary_addr = rsi_leak + 0x36A8` (**empirical** offset, measured under GDB in Docker).
3. **2nd FSB (prompt "from?")** = double write: `fmtstr_payload(6, {got["__stack_chk_fail"]: win, canary_addr: 0x0}, write_size="byte")`
   - writes `win` to `__stack_chk_fail@GOT`,
   - puts `0x00` on canary → at epilogue of `main`, invalid canary triggers `call __stack_chk_fail` → **win()** → flag.

```python
payload = b"%525$p %1$p"           # leak main + rsi (1st FSB)
...
stack_check_fail = elf.got["__stack_chk_fail"]
canary_addr = rsi_addr + 0x36A8
payload = fmtstr_payload(6, {stack_check_fail: win_addr, canary_addr: 0x0}, write_size='byte')  #2nd FSB
```
Flag: `sigpwny{printf_can_change_control_flow}`.

3. **Why __stack_chk_fail and not puts?**

Overwriting `puts@GOT` → `win` creates an **infinite recursion**: `win()` calls `puts()` = becomes `win` → loop → crash. `__stack_chk_fail` is only called if the canary breaks, and `win` does not depend on it → no recursion.

4. **Diff with 05 - Grander Finale**

Grander Finale = Full RELRO → impossible to write the GOT → we overwrite the **saved RIP**. Here **No RELRO** → we prefer the **GOT overwrite of `__stack_chk_fail`** + canary corruption (cleaner than targeting the RIP through the canary).

5. **To remember / pitfalls**

- **`elf.sym` vs `elf.got`** (error #1): to **jump to YOUR function** (`win`) → `elf.sym` (code address). To **hijack the call of a libc function** → `elf.got` (writable box). Here `sym["__stack_chk_fail"]`=0x10f4 (PLT, read-only) ≠ `got["__stack_chk_fail"]`=0x3478 (GOT). Aim for the PLT = write which fails, nothing diverted.
- **Stack offsets = specific to the environment**: the leak of `main` is at `%523$p` in **local-direct** but `%525$p` in **remote/docker**; similarly `canary_addr` = `rsi-0x10f8` (local) vs `rsi+0x36A8` (remote). Reason: what is stacked above `main` (env, argv, loader, libc) shifts the stack → the delta leak→target changes. **Measure in an environment that replicates the remote**: deploy the Dockerfile **with gdb added**, attach, read the real distance. An offset measured locally "works for you" but not on the server.
- **Canary bypassed without the leaker**: we do not read the canary, we **set it to 0** and we **turn its corruption to our advantage** (the check becomes the trigger for `win`). Variant of the “hijack rather than hijack” idea.
- `[!] padding is negative, this will not work on glibc` = warning pwntools benign (order of `%n`); it even appears when the exploit succeeds.
- `buf = 0x1000` bytes = **512 slots** of 8 B → hence very large `%N$p` offsets (~523/525) to exceed the buffer and reach the saved RIP.

## Solve script
Script path: `scripts/pwny.py`
Script path: `scripts/solve.py`

## Flag
sigpwny{printf_can_change_control_flow}

## Lessons and reusable patterns
- Main technique: format-string.
