---
title: "Format-1"
ctf: "Pwny-CTF"
category: "pwn"
difficulty: "Not specified"
points: 250
techniques: ["format-string", "buffer-overflow", "pie-bypass"]
tools: ["netcat", "socat", "gcc", "python"]
keywords: ["Format-1", "Pwny-CTF", "pwn", "format-string", "buffer-overflow", "pie-bypass", "netcat", "socat", "gcc", "python", "aslr", "pie", "padding"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Pwn/Format-1/notes.md"
---

# Format-1 (Pwny-CTF, pwn)

## Summary
Challenge **Format-1** from the Pwny-CTF CTF, pwn category. Main technique: format-string. The name of the challenge can be a trap: first check if the format is really usable (visible leak? useful writing?) before going on a %n/%p attack. The real bug here is just the lack of size limit.

## Statement and artefacts
```nc chal.sigpwny.com 1339```

```
#include <stdlib.h>
#include <unistd.h>
#include <stdio.h>
#include <string.h>

void vuln(char *string)
{
  volatile int target;
  char buffer[64];

  target = 0;

  sprintf(buffer, string);

  if(target == 0xdeadbeef) {
      printf("[REDACTED]\n");
  }
}

int main(int argc, char **argv)
{
  vuln(argv[1]);
}
```

**Author**: Ravi

**Provided files / artifacts:**
- `work/Dockerfile (file, 488 B)`

## Recognition signals
- Signal: The name of the challenge can be a trap: first check if the format is really usable (visible leak? useful writing?) before going on a %n/%p attack. The real bug here is just the lack of size limit.

## Resolution method
1. Read `challenge_prompt.c` — `sprintf(buffer, string)` with `string = argv[1]`, controlled by us via the network; `buffer[64]` and `target` (int) are two adjacent local variables.
2. Understand how `argv[1]` arrives through the network: `Dockerfile` shows a `wrapper.py` (not provided in the challenge files) launched by `socat`, which transforms the **1st line sent** into `argv[1]` (probably via `os.execve`). Confirmed by a `nc` test: one line sent = one complete run, connection closed immediately after, with no output — even with `%p`/`%x`.
3. This last point is key: `sprintf` **never** prints `buffer` or anything else → **no network leakage channels**. Leak techniques using format string (`%N$p` scanner) are therefore useless here, despite the name of the challenge.
4. The real bug: without any `%` in our payload, `sprintf` behaves like a `strcpy` **without limit** — a classic buffer overflow, not a format string. Payload = 64 bytes of padding + `p32(0xdeadbeef)` (32-bit binary, `-m32`), sent directly in one attempt (the offset of 64 was correct on the first try).
5. Remote service directly returns the flag (`sigpwny{thanks_thomas}`) as soon as `target == 0xdeadbeef`.

## Solve script
Script path: [`scripts/challenge_prompt.c`](scripts/challenge_prompt.c)
Script path: [`scripts/solve.py`](scripts/solve.py)

## Flag
sigpwny{thanks_thomas}

## Lessons and reusable patterns
- The name of the challenge can be a trap: first check if the format is really usable (visible leak? useful writing?) before going on a %n/%p attack. The real bug here is just the lack of size limit.
- No network leak channel (nothing is ever displayed) -> no need to try %p/%x to "see" anything; rethink the bug rather than scanning blindly.
- Writing at a fixed relative distance (padding + value) completely ignores PIE and ASLR: only an absolute address would depend on it. Very different from Bug Bounty 6, which needs a leak precisely because it targets an absolute address.
