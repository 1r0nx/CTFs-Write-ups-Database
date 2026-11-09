---
title: "02-Arbitrary-Write"
ctf: "Pwny-CTF"
category: "pwn"
difficulty: "Not specified"
points: 300
techniques: ["format-string", "stack-canary", "pie-bypass"]
tools: ["pwntools", "checksec", "netcat", "python"]
keywords: ["02-Arbitrary-Write", "Pwny-CTF", "pwn", "format-string", "stack-canary", "pie-bypass", "pwntools", "checksec", "netcat", "python", "elf", "canary", "pie"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/PWN-II/02-Arbitrary-Write/notes.md"
---

# 02-Arbitrary-Write (Pwny-CTF, pwn)

## Summary
Challenge **02-Arbitrary-Write** from the Pwny-CTF CTF, pwn category. Main technique: format-string. Redirect rather than hijack: when a fopen/path is globally modifiable and we have an arbitrary write, rewriting this name (often 1 byte is enough) is much simpler than attacking ret — and it bypasses the canary by construction (we don't touch the stack).

## Statement and artefacts
This challenge uses the arbitrary write primitive. Reference the slides!

```nc chal.sigpwny.com 1384```

**Author**: kmh

**Provided files / artifacts:**
- `work/arbitrary_write (file, 16.9 KB)`
- `work/arbitrary_write_patched (file, 16.9 KB)`
- `work/blag.txt (text, 5 B)`

## Recognition signals
- Signal: greet(name) gives arbitrary write via %n.
- Signal: Instead of diverting ret (there is a canary here), we change what fopen will read: blag.txt -> flag.txt.
- Signal: Redirect rather than hijack: when a fopen/path is globally modifiable and we have an arbitrary write, rewriting this name (often 1 byte is enough) is much simpler than attacking ret — and it bypasses the canary by construction (we don't touch the stack).

## Resolution method
1. **The (clever) idea**

- `%n` = **writes** into memory the number of bytes already displayed, at the address provided as an argument → **arbitrary write** primitive.
- No need to overwrite the return address (so **no need to leak/replay the canary**): just rewrite **1 byte** of the global `blag_file`.
- `"blag.txt"` → `"flag.txt"`: only the 1st byte changes, `b` (0x62) → `f` (0x66). A single one-byte write to `&blag_file`.

1. **checksec** → **PIE No**: fixed `&blag_file` = `elf.sym["blag_file"]` (= `0x4040c0`, confirmed by `nm`).
2. **Find the argument index** of the format string → `offset_browser(fmt="p", reconnect=True)`: here **10** (`OFFSET=10`).
3. **Build the write** with pwntools (handles the `%Nc...%OFFSET$hhn` alone):
   ```python
   blag_addr = elf.sym["blag_file"]
   payload = fmtstr_payload(OFFSET, {blag_addr: b"f"}, write_size="byte")  #write 'f' on the 1st byte
   sla(b"?", payload)
   ```
4. **Result**: `print_blag()` now opens `flag.txt` and its `printf(blag)` displays the flag.

See `work/pwny.py`. Continuation: `fmtstr_payload(10, {elf.sym["blag_file"]: b"f"}, write_size="byte")` → `sla("?", payload)` → `print_blag()` reads `flag.txt`.

2. **Flaw**

```c
char blag_file[32];                        // GLOBAL, = "blag.txt"
void print_blag(){ FILE *f = fopen(blag_file,"r"); ... printf(blag); }  // open the file named by the global
void greet(char* name){ printf(name); }    // FORMAT STRING BUG
void main(){ strcpy(blag_file,"blag.txt"); fgets(name,64,stdin); greet(name); print_blag(); }
```
`greet(name)` gives arbitrary write via `%n`. Instead of diverting `ret` (there is a **canary** here), we change what `fopen` will read: `blag.txt` → `flag.txt`.

## Solve script
Script path: [`scripts/pwny.py`](scripts/pwny.py)

## Flag
sigpwny{i_like_`sigpwny.com/pony-site`_more_than_our_current_site}

## Lessons and reusable patterns
- Redirect rather than hijack: when a fopen/path is globally modifiable and we have an arbitrary write, rewriting this name (often 1 byte is enough) is much simpler than attacking ret — and it bypasses the canary by construction (we don't touch the stack).
- %n and variants: %n writes 4 bytes (int), %hn 2 bytes, %hhn 1 byte. Write few bytes = fewer characters to print = shorter and more reliable payload. fmtstr_payload(OFFSET, {addr: val}, write_size="byte") chooses %hhn automatically.
- No PIE makes the target address fixed (elf.sym[...]); otherwise we would have to leak it first.
- There is a 2nd FSB in print_blag (printf(blag)), but the content of the flag has no %, so no display problem.
- In work/pwny.py, the sl(payload) after the sla is a harmless remainder: the program only reads the name once and then terminates (EOF).
