---
title: "GhostBus"
ctf: "2026-hiCTF"
category: "hardware"
difficulty: "hard"
points: null
techniques: ["aes-cbc", "reverse-engineering", "firmware-analysis", "hardware"]
tools: ["objdump", "strings", "python"]
keywords: ["GhostBus", "hiCTF", "hardware", "aes-cbc", "reverse-engineering", "firmware-analysis", "objdump", "strings", "python", "elf", "png", "firmware", "uart", "spi", "aes"]
status: "solved"
has_script: true
source: "hiCTF/hardware/GhostBus/notes.md"
---

# GhostBus (hiCTF, hardware)

## Summary
Challenge **GhostBus** from the hiCTF CTF, hardware category. Main technique: aes-cbc. The GhostBus challenge (hiCTF, hardware) is documented by a resolution note.

## Statement and artefacts
- `capture.vcd` / `capture.csv`: traces 2 channels of the UART bus (ch0 = hub→SE, ch1 = SE→hub).
- `flash_dump.bin`: external SPI NOR flash (1 MiB). Contains MCU firmware (backup copy, linked in `0x08000000`) **and** sealed records.
- `firmware.elf`: MCU firmware (ARM Thumb, stripped) for analysis.
- `diagram.png`: assembly diagram.

**Provided files / artifacts:**
- `ghost_bus.zip (archive, 47.5 KB)`

## Recognition signals
- Signal: Secret nonce exfiltrated by sniffing the internal UART bus (MCU ↔ secure element); key derivation SHA-256(const ‖ nonce) -> AES-256-CBC reconstructed by directly emulating the firmware (Unicorn) rather than guessing the mode.
- Signal: Secure element “locked” but an undocumented UART command (0x10) returns the nonce.
- Signal: Trap: the byte-swap per 32-bit word (impl hard accelerator type) means that AES is not.
- Signal: Harness trap: the 1st Unicorn try gave 2 good blocks + 1 gibberish block -> overlap.
- Signal: Recognize this type: bus VCD/CSV (UART/SPI/I²C) + flash dump + firmware ⇒ secret sniff.
- If we observe SHA-256, think of first words K 428a2f98 71374491 b5c0fbcf … (in LE: 98 2f 8a 42 …).

## Resolution method
1. **Method (step -> command -> what it reveals)**

1. **Decode the UART bus.** Do not rely on CSV (“recover the hidden read”): in-house decoding of the VCD (state machine, bit = 8.7 µs → 115200 bauds). Result identical to CSV → no hidden transaction in the signal; the “hidden read” is the **command `0x10`**.
   - Frame format: `AA 55 | LEN | CMD | DATA[LEN] | CRC16`.
   - ch0: banner `GB2.2 SE OK!` (cmd 0x01) then request `AA 55 00 10 00 7C` (cmd 0x10, read nonce).
   - ch1: `AA 55 10 10` + **16 B nonce** + CRC → **nonce = `9e3b7a44c1d05f82a6e1b4907cd3f5a2`**.
2. **Locate the sealed record.** `strings` flash → `SEALED v2 addr=0x6A000 len=48`, `sealed=0x6A000 len=48`, and a `SEALED v1 rotated out` (old record, decoy).
   - Ciphertext v2 @`0x6A000`, 48 B = `bf4104ca13efeaef33d742378ccff4cc 741ed9df3761005fd530c13789cfd1ca c48087603aa31566bc579f0ac22bdecb`.
3. **Reverse key derivation.** `.rodata` contains **standard** constants: SHA-256 K table (@0x28), S-box AES (@0x128), Rcon + inv-S-box AES (@0x228), plus a custom constant **CONST24 = `04325a9c117f3da0c0ffee5aa55a00ff1234567890abcdef`**.
   - Thumb disassembly (`arm-none-eabi-objdump -M force-thumb`) of `main` @0x8000380: `sha256_init/update/update/final` → **key = SHA256(CONST24 ‖ nonce)** (AES-256).
   - SPI reading (`03 06 A0 00` + 48×`FF`) reads back the sealed 48 B's; byte-swap per 32-bit word; then `AES_setup(ctx, key, iv=nonce)` + `AES_decrypt(ctx, buf,48)`; check **PKCS#7** + `hiCTF{…}`.
4. **Decrypt.** Rather than guessing the mode, **Unicorn emulation** of the firmware's crypto functions (see `work/solve.py`) → `hiCTF{gh0st_bu5_uart_n0nc3_r3v3al_9c3f12}` (+ pad `0x07`×7).

2. **Key concept**

Secret nonce exfiltrated by **sniffing the internal UART bus** (MCU ↔ secure element); key derivation **SHA-256(const ‖ nonce)** → **AES-256-CBC** reconstructed by **directly emulating the firmware** (Unicorn) rather than guessing the mode.

3. **Flaws / to remember**

- Secure element “locked” but an **undocumented UART command (0x10)** returns the nonce: everything that passes on an internal bus is observable (confidentiality ≠ security).
- **Pitfall**: the byte-swap per 32-bit word (impl hard accelerator type) means that AES is not “byte-standard” → naive AES-CBC Python tests fail. **Emulating the firmware** removes any ambiguity (mode, IV, endianness, padding).
- **Harness trap**: the 1st Unicorn try gave 2 good blocks + 1 gibberish block → ctx/buffer memory overlap. Always space and zero-initialize emulation buffers.
- Recognize this type: bus VCD/CSV (UART/SPI/I²C) + flash dump + firmware ⇒ secret sniff, KDF RE, standard decryption.

4. **Recognize crypto constants in a dump**

- SHA-256: first K words `428a2f98 71374491 b5c0fbcf …` (in LE: `98 2f 8a 42 …`).
- AES S-box: `63 7c 77 7b f2 6b 6f c5 30 01 67 2b …`. Rcon: `01 02 04 08 10 20 40 80 1b 36 …`. inv-S-box: `52 09 6a d5 30 36 a5 38 …`.

## Solve script
Script path: [scripts/solve.py](scripts/solve.py)

## Flag
hiCTF{gh0st_bu5_uart_n0nc3_r3v3al_9c3f12}

## Lessons and reusable patterns
- Main technique: aes-cbc.
