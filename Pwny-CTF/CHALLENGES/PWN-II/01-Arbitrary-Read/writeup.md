---
title: "01-Arbitrary-Read"
ctf: "Pwny-CTF"
category: "pwn"
difficulty: "Not specified"
points: 200
techniques: ["format-string", "pie-bypass"]
tools: ["checksec", "netcat", "python"]
keywords: ["01-Arbitrary-Read", "Pwny-CTF", "pwn", "format-string", "pie-bypass", "checksec", "netcat", "python", "elf", "pie", "stack"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/PWN-II/01-Arbitrary-Read/notes.md"
---

# 01-Arbitrary-Read (Pwny-CTF, pwn)

## Summary
Challenge **01-Arbitrary-Read** from the Pwny-CTF CTF, pwn category. Main technique: format-string. Global secret + No PIE = arbitrary read trivial: fixed address -> %N$s on &secret placed in the buffer.

## Statement and artefacts
This challenge uses the arbitrary read primitive. Reference the slides!

```nc chal.sigpwny.com 1382```

**Author**: Kevin Higgs

**Provided files / artifacts:**
- `work/arbitrary_read (file, 16.8 KB)`
- `work/arbitrary_read_patched (file, 16.8 KB)`

## Recognition signals
- Signal: Same printf(name) as 00 - Stack Read, but the flag is no longer on the stack: %lx/%p will never cross it.
- Signal: It must be read via its address.

## Resolution method
1. **Why %s here (even though it crashed in 00)**

- **00**: the bytes of the flag *were* the values on the stack → we read the raw value (`%lx`), `%s` would have dereferenced a non-address.
- **01**: the flag is elsewhere, we provide **ourselves a pointer** (`&flag`) as an argument → `%s` dereferences it correctly = exactly its normal use.

1. **checksec** → `No PIE (0x400000)`: the addresses are **fixed**, so `&flag` is known in advance → `elf.sym["flag"]` (or `nm arbitrary_read | grep flag`).
2. **Find the argument index** of the buffer `name` → `offset_browser(20, prompt="?")`: here **11**.
3. **Build the payload**: the address must fall on an 8-byte aligned slot corresponding to index 11.
   ```python
   payload = b"%11$s" + b"ABC" + p64(elf.sym["flag"])
   #          \_ 5 B. _/ \_3 B./ -> "%11$s"+"ABC" = 8 bytes, so p64 aligned to the 2nd qword of the buffer
   ```
`%11$s` reads arg 11 = this qword = `&flag`, and prints the pointed string.
4. **Send** → `sla(b"?", payload)` → output `Hello sigpwny{wh4t_an_av1d_read3r}` (followed by `ABC` + the address bytes, normal: this is the end of our payload redisplayed).

See `work/pwny.py`. Scrolled: `flag_addr = elf.sym["flag"]` → `sla("?", b"%11$s"+b"ABC"+p64(flag_addr))` → `interactive()`.

2. **Flaw**

```c
char flag[32];                 // GLOBAL (.bss), not on the stack
void greet(char* name){ printf(name); }   // FORMAT STRING BUG
void main(){ char name[64]; read_flag(flag); while(1){ fgets(name,64,stdin); greet(name);} }
```
Same `printf(name)` as 00 - Stack Read, but the flag is **no longer on the stack**: `%lx`/`%p` will never cross it. It must be read via **its address**.

## Solve script
Script path: `scripts/pwny.py`

## Flag
sigpwny{wh4t_an_av1d_read3r}

## Lessons and reusable patterns
- Global secret + No PIE = arbitrary read trivial: fixed address -> %N$s on &secret placed in the buffer.
- Alignment: p64(addr) must start on an 8-byte boundary; we choose N and we padde (%N$s + padding) so that the address falls right on the index slot N. Find N with offset_browser (marker AAAAAAAA).
- \x00 in the address: &flag often ends with null bytes (...40 40 00 00). We put the address at the end of the payload so that fgets (which reads up to \n) is not cut by a \0 in the middle. (fgets is not bothered by \0, but keeping the address last avoids any concerns about alignment with the rest.)
- Recognize: printf(user) + secret declared globally (outside any function) + No PIE -> arbitrary read, not stack read.
