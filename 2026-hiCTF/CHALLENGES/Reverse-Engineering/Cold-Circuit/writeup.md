---
title: "Cold-Circuit"
ctf: "2026-hiCTF"
category: "reverse"
difficulty: "Not specified"
points: null
techniques: ["substitution-cipher", "pie-bypass", "reverse-engineering", "encoding"]
tools: ["gdb", "objdump", "strings"]
keywords: ["Cold-Circuit", "hiCTF", "reverse", "substitution-cipher", "pie-bypass", "reverse-engineering", "encoding", "gdb", "objdump", "strings", "elf", "zip", "hex", "pie"]
status: "solved"
has_script: false
source: "hiCTF/Reverse-Engineering/Cold-Circuit/notes.md"
---

# Cold-Circuit (hiCTF, reverse)

## Summary
Challenge **Cold-Circuit** from the hiCTF CTF, reverse category. Main technique: substitution-cipher. “A small standalone checker, check, decides whether a flag is right. »; cold-circuit.zip -> check (SHA-256 compliant zip).

## Statement and artefacts
“A small standalone checker, check, decides whether a flag is right. »; cold-circuit.zip -> check (SHA-256 compliant zip).

**Provided files / artifacts:**
- `cold-circuit.zip (archive, 3.6 KB)`

## Recognition signals
- Signal: substitution-permutation network (SPN) of which all tables are in.rodata -> we reverse the turns from the target; ptrace anti-debug trap.
- Signal: Recognize: loop of turns with addition of key + reading in a table of 256 B + writing to an index taken from a table of 16 B = SPN “house”. If the tables are clear in the binary, no need for a secret key: we reverse.
- Signal: Trap: under debugger, ptrace changes the key of the 1st round -> a correct flag would be refused in gdb. Prefer static analysis (or neutralize ptrace).

## Resolution method
1. **How the binary works (read in the disassembly)**

| Address | Role |
|---|---|
| `0x12d6` (parse) | length **39**; prefix `hiCTF{`; last character `}`; 32 characters **hex** (`0x1283`: 0-9, a-f, A-F) → 16 bytes |
| `0x1538` | `ptrace(PTRACE_TRACEME)`: if failure with `EPERM` (debugger present) → flag `traced` |
| `0x1584` / `0x125c` | decoy: `(v²+1) % 4 == 0` with `v = argc + octet0` → **impossible** (a square is 0 or 1 mod 4) → dead “unreachable” branch |
| `0x15cc` / `0x1229` | `(v² % 4)!= 2` → always true |
| `0x15f8` | copy of **20 turn keys** × 16 B from `0x2140`; if `traced` → `key[0][0] ^= 1` (the correct flag fails under gdb) |
| `0x1623`-`0x173f` | **20 turns**: `st[i] += key[r][i]` → `st[i] = SBOX[st[i]]` (`0x2020`) → `out[PERM[i]] = st[i]` (`0x2120`) |
| `0x175f` | compares to target 16 B (`0x2280`) → “Access granted. » |

1. `file`, `strings` → ELF stripped, `ptrace`, `memcmp`, `hiCTF{`, “Access granted. ".
2. `objdump -d -M intel` → structure above.
3. Check that S-box and permutation are **bijections** (otherwise no unique inverse) → OK.
4. GB back from the target: for r = 19 → 0: inverse permutation, inverse S-box, subtraction of the key.
5. **Check**: `./check 'hiCTF{6e30…2121}'` → `Access granted.` (exit 0), in argument and on stdin; a modified character → `Incorrect.`

## Flag
hiCTF{6e305f6a7461675f6e65656465642121}

## Lessons and reusable patterns
- Recognize: loop of turns with addition of key + reading in a table of 256 B + writing to an index taken from a table of 16 B = “house” SPN. If the tables are clear in the binary, no need for a secret key: we reverse.
- Trap: under debugger, ptrace changes the key of the 1st round -> a correct flag would be refused in gdb. Prefer static analysis (or neutralize ptrace).
- “Unreachable” branches based on impossible arithmetic properties (mod 4 squares) are decoys: check them on paper rather than following them.
- In.rodata of a non-relocated PIE, virtual address = file offset (check with objdump -h).
