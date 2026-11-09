---
title: "C3-Vault"
ctf: "2026-hiCTF"
category: "hardware"
difficulty: "Not specified"
points: null
techniques: ["disk-forensics", "reverse-engineering", "firmware-analysis", "hardware"]
tools: ["capstone", "esptool", "python"]
keywords: ["C3-Vault", "hiCTF", "hardware", "disk-forensics", "reverse-engineering", "firmware-analysis", "capstone", "esptool", "python", "png", "firmware", "spi", "efuse", "aes"]
status: "solved"
has_script: true
source: "hiCTF/hardware/C3-Vault/notes.md"
---

# C3-Vault (hiCTF, hardware)

## Summary
Challenge **C3-Vault** from the hiCTF CTF, hardware category. Main technique: disk-forensics. ESP32-C3 gateway removed from service, SPI flash + eFuse read window preserved. “Recover its enrollment credentials and convince the live service that you are the gateway. » The flag only exists on the live service (--ssl …:1337), not in evidence.

## Statement and artefacts
ESP32-C3 gateway removed from service, SPI flash + eFuse read window preserved. “Recover its enrollment credentials and convince the live service that you are the gateway. » The flag only exists on the live service (--ssl …:1337), not in evidence.

**Provided files / artifacts:**
- `c3_vault.zip (archive, 4.2 MB)`
- `work/ATTRIBUTION.txt (text, 468 B)`
- `work/README.txt (text, 488 B)`
- `work/SHA256SUMS (file, 1.3 KB)`
- `work/app_dec.bin (binary/data, 1.0 MB)`
- `work/diagram.png (image, 65.2 KB)`
- `work/efuse_read.bin (binary/data, 336 B)`
- `work/flash_image.bin (binary/data, 4.0 MB)`
- `work/nvs_keys_dec.bin (binary/data, 4.0 KB)`
- `work/nvs_plain.bin (binary/data, 24.0 KB)`
- `work/ptable_dec.bin (binary/data, 4.0 KB)`
- `work/recovery.txt (text, 876 B)`
- `work/segs.pkl (file, 86 B)`

## Recognition signals
- Signal: Recovery chain: Flash Encryption key (eFuse) -> decrypt partition table and nvs_keys -> NVS Encryption key -> decrypt NVS (credentials) -> replay auth protocol (disassembled from firmware).
- Signal: Enc Flash Trap: XTS in blocks of 128 B, bytes inverted before/after, tweak = LE32(addr & ~0x7F).
- Signal: NVS trap: only the entries are encrypted (XTS-256, tweak = offset), header/bitmap in clear -> readable seq.

## Resolution method
1. **Method (step -> command -> what it reveals)**

1. **eFuse**: 336 B = 84 words. recovery.txt: BLOCK0/1 = 6 words, BLOCK2..10 = 8 words → **BLOCK4 = BLOCK_KEY0** at offset **0x70**. KEY_PURPOSE_0 = 4 (XTS_AES_128) in BLOCK0 word2 (`0x04040000`).
   Key = `a60e11f7…4d7f` (32 B).
2. **Flash Encryption** (XTS-AES-128, algo esptool): table @0x8000 unreadable → encrypted. The correct key is **INVERTED BLOCK_KEY0** (`[::-1]`) — verified by the magic `AA50` of the table (`keytest.py`). `esp_flash_dec.py`: table → `nvs`@0x9000(0x6000), `nvs_keys`@0xf000(flags=1, encrypted), `factory`@0x10000.
3. **NVS Encryption**: NVS pages in clear (header+bitmap) but **encrypted entries** → NVS encryption active. `nvs_keys` decrypted (flash enc) = eky(32)‖tky(32). NVS entries = **XTS-AES-256**, eky‖tky key, **tweak = partition entry offset** (LE32), first 64 page bytes unencrypted (`nvs_decrypt.py`).
4. **Credentials** (`nvs_full.py`):
   - ns `gateway`: `device_id`=`ee0315f3953aad298d7f3f43973ad618`, `generation`=**7**, hostname `c3-vault-gw`.
   - ns `vault_v2` (current): `seed`=`826e4e9e…83c5`.
   - ns `vault_v1` (**expired = decoy**): `seed`=`d857200f…aa4f`. The firmware opens `vault_v2` in READONLY.
5. **Firmware** (`factory` decrypted): ESP image, seg3 = IROM code @0x42000020. RISC-V capstone disassembly (`disas.py`, `dump_region.py`) of functions referencing `c3-vault/device-key/v2` and `C3VAULT-AUTH-V2`:
   - memcpy = ROM `0x40000358`; `mbedtls_md_info_from_type(SHA256)` + `mbedtls_md_hmac`.

2. **Reconstructed auth protocol (the core)**

```
device_key = HMAC-SHA256(seed_v2, "c3-vault/device-key/v2\0"(23) ‖ device_id(16) ‖ generation_LE32)
response   = HMAC-SHA256(device_key,"C3VAULT-AUTH-V2\0"(16)      ‖ challenge(32)  ‖ device_id(16))
```
(labels **include `\0`** — lengths 23 and 16 read in code; generation serialized as **little-endian**.)

Service: `C3VAULT/2 READY` → `CHALLENGE <64hex>`; we answer `AUTH <64hex>` → `VAULT OPENED` + flag. Full solver: `work/solve.py` (TLS, SNI required).

3. **Key concept**

**Recovery chain**: Flash Encryption key (eFuse) → decrypt partition table and `nvs_keys` → NVS Encryption key → decrypt NVS (credentials) → **replay auth protocol** (disassembled from firmware).

## Solve script
Script path: [scripts/conn.py](scripts/conn.py)
Script path: [scripts/disas.py](scripts/disas.py)
Script path: [scripts/dump_region.py](scripts/dump_region.py)
Script path: [scripts/esp_flash_dec.py](scripts/esp_flash_dec.py)
Script path: [scripts/esp_img.py](scripts/esp_img.py)
Script path: [scripts/keytest.py](scripts/keytest.py)
Script path: [scripts/nvs_decrypt.py](scripts/nvs_decrypt.py)
Script path: [scripts/nvs_full.py](scripts/nvs_full.py)
Script path: [scripts/nvs_parse.py](scripts/nvs_parse.py)
Script path: [scripts/parse_ptable.py](scripts/parse_ptable.py)
Script path: [scripts/solve.py](scripts/solve.py)

## Flag
hiCTF{efus3_cl34r_jt4g_0p3n_nv5_1936cba275}

## Lessons and reusable patterns
- Recognize: eFuse dump + unreadable ESP flash = Flash Encryption XTS-AES; eFuse key to reverse.
- Enc Flash Trap: XTS in blocks of 128 B, bytes reversed before/after, tweak = LE32(addr & ~0x7F).
- NVS trap: only the entries are encrypted (XTS-256, tweak = offset), clear header/bitmap -> readable seq.
- Decoy: expired namespace vault_v1; the flag (efuse_clear jtag_open nvs) describes the bad configs exploited.
- HMAC null-terminated labels in the message: detail seen only during disassembly (lengths 23/16).
