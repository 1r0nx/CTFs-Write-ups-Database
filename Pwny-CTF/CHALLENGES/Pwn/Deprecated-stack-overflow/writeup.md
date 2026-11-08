---
title: "Deprecated-stack-overflow"
ctf: "Pwny-CTF"
category: "pwn"
difficulty: "Not specified"
points: 100
techniques: ["format-string", "buffer-overflow"]
tools: ["netcat"]
keywords: ["Deprecated-stack-overflow", "Pwny-CTF", "pwn", "format-string", "buffer-overflow", "netcat", "stack", "padding"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Pwn/Deprecated-stack-overflow/notes.md"
---

# Deprecated-stack-overflow (Pwny-CTF, pwn)

## Summary
Challenge **Deprecated-stack-overflow** from the Pwny-CTF CTF, pwn category. Main technique: format-string. Recognize: gets() (or scanf("%s"), strcpy) + a sensitive variable declared just after a buffer -> overflow of an adjacent variable, no need to reach the return address.

## Statement and artefacts
Can you pwn this program? Look in challenge.c for hints!

`nc chal.sigpwny.com 1374`

**Provided files / artifacts:**
- `work/Dockerfile (file, 580 B)`
- `work/challenge (file, 19.4 KB)`

## Recognition signals
- Signal: Read the condition:!= 0 -> overwriting with anything is enough (no need for exact value). If it was == 0xcafebabe, it would take p64(.) at the correct offset (see 1 - Manipulate / Bug Bounty 2).

## Resolution method
1. **Binary**

- `main()`: `char name[32];` then `uint64_t number = 0;` immediately after on the stack. Read by **`gets(name)`** (no size limit).
- Victory: `if (number!= 0) print_flag();`. `print_flag()` reads and displays `flag.txt`.
- The source gives everything: comment *"8 byte number which exists after the 32 bytes of name"* + *"What happens when we put (a lot) more than 32 characters?"*.

1. `gets` having **no bounds**, everything you type beyond 32 bytes overflows onto `number`.
2. Send **≥ 33 characters** (here a long series of `f`): the bytes of `number` change from `0` to non-zero.
3. Condition `number!= 0` satisfied → the flag is displayed.

```bash
# in one line
python3 -c "print('A'*40)" | nc chal.sigpwny.com 1374
```

## Flag
sigpwny{nice_work_and_please_dont_use_gets}

## Lessons and reusable patterns
- Recognize: gets() (or scanf("%s"), strcpy) + a sensitive variable declared just after a buffer -> overflow of an adjacent variable, no need to reach the return address.
- Read the condition:!= 0 -> overwriting with anything is enough (no need for exact value). If it was == 0xcafebabe, it would take p64(...) at the correct offset (see 1 - Manipulate / Bug Bounty 2).
- Offset here = 32 bytes of name (no additional alignment padding before number, contiguous variables).
- Almost identical variant already processed: 0 - Overflow. The flag itself recalls the lesson: please_dont_use_gets.
