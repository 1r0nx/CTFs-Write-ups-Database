---
title: "ELF-x86-Stack-buffer-overflow-basic-1"
ctf: "Root-Me"
category: "App-System"
difficulty: "easy"
points: 5
techniques: ["buffer-overflow", "ret2win"]
tools: ["pwntools", "gdb"]
keywords: ["ELF-x86-Stack-buffer-overflow-basic-1", "Root-Me", "app-system", "stack-overflow"]
status: "solved"
has_script: true
source: "Root-Me/App-System/ELF-x86-Stack-buffer-overflow-basic-1/ (no notes)"
---

# ELF-x86-Stack-buffer-overflow-basic-1 (Root-Me, App-System)

## Summary

Challenge **ELF-x86-Stack-buffer-overflow-basic-1** from the Root-Me CTF, app-system category. A basic x86 stack buffer overflow that redirects execution to a win function.

## Statement and artefacts

**Official statement (Root-Me, English page):**

**Environment configuration:**

| Protection | Description | Enabled |
|---|---|---|
| PIE | Position Independent Executable | No |
| RelRO | Read Only relocations | No |
| NX | Non-Executable Stack | No |
| Heap exec | Non-Executable Heap | No |
| ASLR | Address Space Layout Randomization | No |
| SF | Source Fortification | No |
| SRC | Source code access | Yes |

**Source code:**

```c
#include <unistd.h>
#include <sys/types.h>
#include <stdlib.h>
#include <stdio.h>

int main()
{
    int var;
    int check = 0x04030201;
    char buf[40];

    fgets(buf,45,stdin);

    printf("\n[buf]: %s\n", buf);
    printf("[check] %p\n", check);

    if ((check != 0x04030201) && (check != 0xdeadbeef))
        printf ("\nYou are on the right way!\n");

    if (check == 0xdeadbeef)
    {
       printf("Hell yeah! You win!\nOpening your shell...\n");
       setreuid(geteuid(), geteuid());
       system("/bin/bash");
       printf("Shell closed! Bye.\n");
    }
    return 0;
}
```

**Challenge connection information:**
- Host: `challenge02.root-me.org`
- Protocol: `SSH`
- Port: `2222`
- SSH access: `ssh -p 2222 app-systeme-ch13@challenge02.root-me.org`
- Username: `app-systeme-ch13`
- Password: `app-systeme-ch13`

- **Category:** App - System
- **Difficulty:** Very easy
- **Points:** 5
- **Author(s):** Lyes
- **Published:** 2015-03-25 18:36:14
- **Root-Me page:** https://www.root-me.org/en/Challenges/App-System/ELF-x86-Stack-buffer-overflow-basic-1

**Provided file (as listed on Root-Me):**
- [`b01debb4a5b7552092f47c50e50aee80.txt`](https://www.root-me.org/local/cache-code/b01debb4a5b7552092f47c50e50aee80.txt) — source-code download listed on the challenge page.

## Recognition signals

- Signal: a 32-bit ELF binary reading input into a fixed-size stack buffer.
- Signal: an obvious target address (`0xdeadbeef`) to place in the saved return address.

## Resolution method

1. Connect to the remote service with SSH using the provided credentials.
2. Send a payload of 40 bytes of padding followed by the target address encoded little-endian with `p32(0xdeadbeef)`.
3. Keep the shell interactive to read the flag.

## Solve script

Script path: [`scripts/solve.py`](scripts/solve.py)

## Flag

1w4ntm0r3pr0np1s

## Lessons and reusable patterns

- Classic x86 ret2win: compute the offset to the saved return address, then overwrite it with the address of the winning function.
