---
title: "Integer-Overflow"
ctf: "Pwny-CTF"
category: "pwn"
difficulty: "Not specified"
points: 150
techniques: ["buffer-overflow", "integer-overflow"]
tools: ["pwntools", "netcat", "python"]
keywords: ["Integer-Overflow", "Pwny-CTF", "pwn", "buffer-overflow", "pwntools", "netcat", "python", "heap"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/PWN-I/Integer-Overflow/notes.md"
---

# Integer-Overflow (Pwny-CTF, pwn)

## Summary
Challenge **Integer-Overflow** from the Pwny-CTF CTF, pwn category. Main technique: buffer-overflow. Recognize: a small and/or unsigned integer type (uint8_t, int8_t, short…) + a condition that cannot be reached “normally” -> think overflow / wrap-around, not stack overflow.

## Statement and artefacts
`i` is an 8-bit unsigned number, which means it can hold `2^8 = 256` possible values, from `0` to `255` inclusive. `atoi` will convert your input to an integer. If you try to store something greater than `256` into an 8-bit unsigned integer, it'll wrap around!

So, the question is, what value of `x` will cause `50 + x > 256` but also `50 + x < 256 + 50`?

```nc chal.sigpwny.com 1342```

```
#include <stdlib.h>
#include <unistd.h>
#include <stdio.h>
#include <string.h>
#include <stdint.h>

void vuln(char *string)
{
  uint8_t i = 50;
  i += atoi(string);
  if (atoi(string) < 0) {
    printf("Nice try, no negative numbers!\n");
    return;
  }
  if (i < 49)
  printf("[flag]\n");
}

int main(int argc, char **argv)
{
  vuln(argv[1]);
}
```

- `vuln(argv[1])`: `uint8_t i = 50;` then `i += atoi(string);`.
- Guardrail: `if (atoi(string) < 0) return;` → **negatives are refused**.
- Victory: `if (i < 49) printf(flag);`.
- No binary provided: the remote service passes the **line sent to stdin to `argv[1]`**.

**Provided files / artifacts:**

## Recognition signals
- Signal: Trap: atoi is called twice (once for i +=, once for test < 0). Same input -> same result, therefore no impact here, but to be noted (a value which changes between two readings could create a TOCTOU).

## Resolution method
1. **The reasoning**

- `i` is 8 bits → `i = (50 + x) mod 256`. Beyond 255, it **starts back to 0**.
- Without overflow it is impossible: `50 + x` with `x >= 0` always makes `>= 50`, never `< 49`.
- We must therefore **loop** `i`: `50 + x >= 256`, and after the modulo remain `< 49`.
  - Window: `256 <= 50 + x <= 304`, or **`206 <= x <= 254`**.
- `x = 206` → `50 + 206 = 256` → `256 & 0xff = 0` → `0 < 49` → flag.

1. Calculate the winning window (above), take `x = 206`.
2. `(echo "206"; sleep 1) | nc chal.sigpwny.com 1342` → the service returns the flag.

```bash
(echo "206"; sleep 1) | nc chal.sigpwny.com 1342
# -> sigpwny{go_with_the_fl0w}
```

`work/solve.py` does the same thing in pwntools (`sendline(b"206")`).

## Solve script
Script path: [`scripts/solve.py`](scripts/solve.py)

## Flag
sigpwny{go_with_the_fl0w}

## Lessons and reusable patterns
- Recognize: a small and/or unsigned integer type (uint8_t, int8_t, short…) + a condition that cannot be reached “normally” -> think overflow / wrap-around, not stack overflow.
- uint8_t: range 0..255, arithmetic modulo 256. 255 + 1 = 0. (Signed: int8_t goes -128..127, 127 + 1 = -128.)
- The guard atoi < 0 closes the “negative number” channel; wrap-around is the only path remaining.
- Trap: atoi is called twice (once for i +=, once for test < 0). Same input -> same result, therefore no impact here, but to be noted (a value which changes between two readings could create a TOCTOU).
- Harder variant in CTF: overflow on a size/length (malloc(n*size) which loops -> heap too small), or signed int used as negative index after wrap.
