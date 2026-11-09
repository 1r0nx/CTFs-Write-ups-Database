---
title: "Bug-Bounty-4"
ctf: "Pwny-CTF"
category: "pwn"
difficulty: "Not specified"
points: 250
techniques: ["encoding"]
tools: ["netcat", "python"]
keywords: ["Bug-Bounty-4", "Pwny-CTF", "pwn", "encoding", "netcat", "python", "elf", "hex"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/PWN-I/Bug-Bounty-4/notes.md"
---

# Bug-Bounty-4 (Pwny-CTF, pwn)

## Summary
Challenge **Bug-Bounty-4** from the Pwny-CTF CTF, pwn category. Main technique: encoding. Fgets(buf, N, stdin) is not automatically safe: it limits the size, but if N > sizeof(buf), the overflow still exists. Always compare the size given to fgets with the actual size of the buffer.

## Statement and artefacts
Maybe if we don't use `gets` we'll be safe?

Bug bounty: ONE MILLION DOLLARS!!!!

`nc chal.sigpwny.com 1346`

**author**: Akhil

**Provided files / artifacts:**
- `work/Makefile (file, 126 B)`
- `work/challenge (file, 19.8 KB)`
- `work/challenge_patched (file, 19.8 KB)`

## Recognition signals
- Signal: The program no longer uses gets() (no more infinite limit), but fgets(name, 64,.) still accepts 64 bytes in a buffer of 48: 16 bytes of overflow, enough to overwrite value and ptr.
- Signal: The real danger is not the overflow itself, but what the program does afterwards: if ptr is no longer NULL, it writes value to the address pointed to by ptr.
- Signal: By controlling both, we have a complete write-what-where.
- Signal: all_leaks = [hex(i) for i in all_leaks] transformed the list of integers into a list of text strings, so all_leaks[-2] became a str instead of an int.
- If we observe p64() requires a real integer, think of struct.error: required argument is not an integer.
- Signal: Correction: never reassign all_leaks with hex(), make the display readable on a separate variable (log.info([hex(i) for i in all_leaks])).

## Resolution method
1. Notice that `gets()` has disappeared but that the real danger is `*ptr = value` just after the overflow (the free clue confirms this: *"Are there other variables you can control?"*).
2. The program displays the address of each variable on the stack (`name`, `value`, `ptr`, return address) before **and** after entry, exactly like the previous challenges.
3. `leak_hex_int()` extracts all displayed hex addresses. `all_leaks[-2]` retrieves the address from the **return address** box (penultimate address displayed).
4. Build the payload: 48 bytes of padding for `name`, then the two variables in the actual order in memory (not necessarily the order of the source code):
   - `ptr` ← address of the “return address” box (where to write)
   - `value` ← address of `print_flag` (what to write)
5. At runtime, `*ptr = value` writes the address of `print_flag` directly to the return address → to `ret` of `vuln()`, the program jumps into `print_flag()` → flag.

```python
all_leaks = leak_hex_int(output, True)   # list of INTEGER, never reassign it to hex()!
print_flag_addr = elf.sym["print_flag"]
return_addr = all_leaks[-2]              # address in the “return address” box
payload = b"A" * 48 + p64(return_addr) + p64(print_flag_addr)
```

1. **Order ready**

```bash
./pwny.py --remote --host chal.sigpwny.com --port 1346
```

2. **Flaw**

```c
uint64_t value = 0xdeadbeef;
uint64_t *ptr = NULL;
char name[48];

fgets(name, 64, stdin);   // overflow: 64 > 48, overwrites value and ptr

if (ptr) {
    *ptr = value;         // arbitrary writing if ptr!= NULL
}
```
The program no longer uses `gets()` (no more infinite limit), but `fgets(name, 64,...)` still accepts 64 bytes in a buffer of 48: 16 bytes of overflow, enough to overwrite `value` and `ptr`.

The real danger is not the overflow itself, but what the program does **after**: if `ptr` is no longer `NULL`, it writes `value` to the address pointed to by `ptr`. By controlling both, we have a complete **write-what-where**.

3. **Script bug encountered (excluding challenge)**

`all_leaks = [hex(i) for i in all_leaks]` transformed the list of integers into a list of **text strings**, so `all_leaks[-2]` became a `str` instead of a `int`. `p64()` requires a real integer → `struct.error: required argument is not an integer`. Correction: never reassign `all_leaks` with `hex()`, make the display readable on a separate variable (`log.info([hex(i) for i in all_leaks])`).

## Solve script
Script path: [scripts/pwny.py](scripts/pwny.py)

## Flag
sigpwny{the_only_safe_code_is_no_code}

## Lessons and reusable patterns
- fgets(buf, N, stdin) is not automatically safe: it limits the size, but if N > sizeof(buf), the overflow still exists. Always compare the size given to fgets with the actual size of the buffer.
- Write-what-where: as soon as the code does a dereference (*ptr =...) on a variable that the overflow can reach, it is an arbitrary write primitive much more powerful than overwriting a single variable.
- The actual order of variables in memory may differ from the order of declaration in the source code: rely on the stack drawing provided by the program, not the C code alone.
- Python trap: hex(i) returns a str. Never overwrite a list of integers that you are going to reuse for binary (p64, p32...) with its text version.
