---
title: "0byte"
ctf: "2026-battleCTF"
category: "misc"
difficulty: "Not specified"
points: 50
techniques: ["xor-cipher", "deserialization", "zip-cracking", "reverse-engineering", "encoding", "malware-analysis", "vm-reverse"]
tools: ["pwntools", "radare2", "readelf", "strings", "capstone", "unzip", "7z", "python"]
keywords: ["0byte", "battleCTF", "misc", "xor-cipher", "deserialization", "zip-cracking", "reverse-engineering", "encoding", "malware-analysis", "vm-reverse", "pwntools", "radare2", "readelf", "strings", "capstone", "unzip"]
status: "solved"
has_script: true
source: "battleCTF/CHALLENGES/out-context/0byte/notes.md"
---

# 0byte (battleCTF, misc)

## Summary
Challenge **0byte** from the battleCTF CTF, misc category. Main technique: xor-cipher. The "malicious" binary only downloads PuTTY ("out of context"). The real challenge is a Russian doll of formats (zip AES / PE / base64 / gzip / pickle / hex / nibble-swap / ELF) terminated by a small BMI2 VM whose output is deliberately hidden by a write decoy.

## Statement and artefacts
Format: battleCTF{....}

**Provided files / artifacts:**
- `work/0byte.exe (binary, 828.5 KB)`
- `work/0byte.zip (archive, 289.2 KB)`
- `work/drop.b64 (file, 913 B)`
- `work/drop.pickle (file, 17.6 KB)`
- `work/file (file, 17.6 KB)`
- `work/flag.elf (binary, 8.8 KB)`
- `work/hash.txt (text, 578.2 KB)`

## Recognition signals
- Signal: The.text calculates the flag byte by byte in the output buffer (0x402018.0x40202f) with BMI2 pext / pdep instructions, a mask and constants, plus some xor / popcnt.
- Signal: FINAL TRAP: the full flag is written in output (0x402018), but the final write displays message (0x402008), i.e. the decoy banner "Here We GB.!".
- Signal: Running the binary therefore does NOT display the flag.
- Signal: The calculated output buffer must be read.
- Signal: Unicorn 2.1.2 does not support pext/pdep, so we reimplement the logic in Python (or we patch the write to point to 0x402018, or we execute on a BMI2 CPU after repointing).

## Resolution method
1. **The zip: password infected**

`0byte.zip` is AES encryption (WinZip AE-1), it contains `0byte.exe`.

```sh
unzip -l 0byte.zip          #-> 0byte.exe, method=AES Encrypted
7z l -slt 0byte.zip         # Method = AES-256 Deflate
```

The password should not be bruteforced: `infected` is the **convention** used everywhere to share a malware sample (VirusShare, MalwareBazaar, AV labs). The name "0byte" + the sharing on Discord points towards this convention.

```sh
7z x -pinfected 0byte.zip
file 0byte.exe   # PE32+ x86-64, MinGW GCC 8.1.0, 9 sections
```

2. **The PE: a downloader that recovers PuTTY**

Notable imports: `InternetOpenA` / `InternetOpenUrlA` / `InternetReadFile` (WININET) + `CreateProcessA`. User-Agent = `Downloader`. Classic downloader/dropper.

The URLs are not in the clear: they are stored in **arrays of dwords** (1 dword = 1 character, low byte) and assembled at runtime. By disassembling / emulating (Unicorn) the routine which constructs these chains, we recover:

- C2 / config: `https://bugpwn.com/drop.ini`
- payload real: `https://the.earth.li/~sgtatham/putty/latest/w32/putty.exe` (the real PuTTY)
- deposit file: `08914b150cdd6888bf32d668c9336169.exe`

The binary downloads PuTTY, writes it under that name and launches it via `CreateProcessA`. It never "prints" a flag: the flag is dimension **C2** (`drop.ini`).

RE Tip: `strings` doesn't do anything useful. You have to disassemble (capstone / radare2) and locate the `movabs` which mount the chains on the stack, or emulate the function.

3. **drop.ini: base64 -> gzip -> pickle -> hex**

Content retrieved at `https://bugpwn.com/drop.ini` = a large base64 blob starting with `H4sI` (= magic gzip in base64).

```python
import base64, gzip, pickle
raw  = base64.b64decode(open("drop.b64","rb").read())
blob = gzip.decompress(raw)          # starts with \x80\x04\x95 -> pickle protocol 4
```

WARNING: decompressing via a pipe shell (`| gunzip`) **truncates** the output. Use `gzip.decompress` in Python to get the full 18050 bytes.

The pickle: NEVER do `pickle.loads` on unreliable data (code execution). We check it first with `pickletools.dis`: here a single opcode `BINBYTES`, no `GLOBAL`/`REDUCE` -> harmless, it's just a `bytes` object.

```python
import pickletools, io
pickletools.dis(blob, io.StringIO())   #-> PROTO 4 / FRAME / BINBYTES (safe)
obj = pickle.loads(blob)               # safe: BINBYTES only
hexs = obj.decode()                    # a long hexadecimal string
payload = bytes.fromhex(hexs)          #9016 bytes
```

4. **payload -> ELF64 (nibble-swap + reverse)**

`payload` has no recognized magic. But by **reversing the nibbles of each byte** (`(b<<4)|(b>>4)`) we see section names/ELF symbols appear, written backwards (`ssb.` -> `.bss`, `batrtshs.` -> `.shstrtab`, + `message`, `mask`, `output`, `flag.asm`). So the file is **nibble-swappe AND reverse in byte order**.

```python
def ns(b): return bytes(((x<<4)|(x>>4))&0xff for x in b)
elf = ns(payload)[::-1]                #-> starts with 7f 45 4c 46 = ELF64
open("flag.elf","wb").write(elf)
```

```sh
readelf -h flag.elf   # ELF64 EXEC x86-64, entry 0x401000
readelf -s flag.elf   # symbols: mask@0x402000, message@0x402008, msg_len=0xf, output@0x402018(.bss)
readelf -x .data flag.elf
#  0x402000 ba ba ba b0 00 00 00 00 <- mask (qword)
#  0x402008 "Here We GB...!\n" <- message (15 bytes) = LURE
```

5. **The ELF: a BMI2 mini-VM, and a write trap**

The `.text` calculates the flag byte by byte in the `output` buffer (0x402018..0x40202f) with **BMI2** instructions `pext` / `pdep`, a mask (`mask`) and constants, plus some `xor` / `popcnt`. Example:

```asm
mov   rax, [0x402000]        ; rax = mask = 0x00000000B0BABABA
mov   ebx, 0x890
pext rcx, rbx, rax; mask-guided bit extraction
mov [0x40201f], cl; writes a byte of the flag
... ; same for 0x40201e, 0x40201d, ...
mov   byte [0x40202a], 0x6e  ; 'n' en dur
mov   ebx, 0x1337
popcnt rcx, rbx              ; = 9
add   rcx, 0x3d              ; -> 0x46 = 'F'
```

FINAL TRAP: the full flag is written in `output` (0x402018), but the final `write` displays `message` (0x402008), i.e. the decoy banner "Here We GB...!":

```asm
mov eax,1 ; mov edi,1 ; mov rsi,0x402008 ; mov edx,0xf ; syscall   ; write(1, message, 15)
mov eax,0x3c ; xor rdi,rdi ; syscall                                ; exit(0)
```

Running the binary therefore does NOT display the flag. You must read the calculated buffer `output`. Unicorn 2.1.2 does not support `pext`/`pdep`, so we reimplement the logic in Python (or we patch the `write` to point to 0x402018, or we execute on a BMI2 CPU after repointing).

## Solve script
Script path: `scripts/solve.py`

## Flag
battleCTF{DespairEnergy}

## Lessons and reusable patterns
- Main technique: xor-cipher.
