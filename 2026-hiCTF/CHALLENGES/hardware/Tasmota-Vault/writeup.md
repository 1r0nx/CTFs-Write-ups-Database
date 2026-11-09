---
title: "Tasmota-Vault"
ctf: "2026-hiCTF"
category: "hardware"
difficulty: "Not specified"
points: null
techniques: ["pcap-analysis", "disk-forensics", "reverse-engineering", "hardware", "encoding", "vm-reverse"]
tools: ["python"]
keywords: ["Tasmota-Vault", "hiCTF", "hardware", "pcap-analysis", "disk-forensics", "reverse-engineering", "encoding", "vm-reverse", "python", "pcap", "tcp", "aes", "hex", "nonce", "gcm"]
status: "solved"
has_script: true
source: "hiCTF/hardware/Tasmota-Vault/notes.md"
---

# Tasmota-Vault (hiCTF, hardware)

## Summary
Challenge **Tasmota-Vault** from the hiCTF CTF, hardware category. Main technique: pcap-analysis. The Tasmota-Vault challenge (hiCTF, hardware) is documented by a resolution note.

## Statement and artefacts
- `flash.bin`: ESP32 4 MiB flash image (physical offsets preserved).
- `mqtt.pcap`: courtesy broker session (Ethernet/IPv4/TCP/MQTT 3.1.1), historical state + retransmission.
- `recovery.txt` / `ATTRIBUTION.txt`: hypotheses + pinned Tasmota v15.6.0 source (contains Berry).

**Provided files / artifacts:**
- `tasmota_vault.zip (archive, 55.6 MB)`

## Recognition signals
- Signal: Extraction of a LittleFS partition from an ESP32 flash image, **decompilation of the Berry v4 (custom agent) bytecode to reconstruct the KDF, then AES-256-GCM decryption** of the sealed record with the correct epoch/nonce found in the MQTT traffic (the valid GCM tag).
- If we observe Security is based on the secret of the keyring in flash, thinking about who reads the flash replays no matter.
- Signal: No brute force: the AES-GCM tag is an oracle of validity -> we test the rotations.
- If we observe Pitfalls: misleading partition label (spiffs, think of LittleFS); message retained (epoch 7).
- Signal: bytes().add(n, 4) = little-endian integer on 4 B; bytes("00") = parsing hex -> \x00.
- If we observe Recognize this type, think about flash image of an IoT device + network capture ⇒ extract the FS.

## Resolution method
1. **Method (step -> command -> what it reveals)**

1. **ESP32 partition table** (@`0x8000`): partition `spiffs` @`0x3b0000` size `0x50000`. The label is (`recovery.txt`): it is actually **LittleFS 2.0, block 4096** (80 blocks).
2. **Mount LittleFS** (`littlefs-python`, `block_size=4096 block_count=80`) → files: `autoexec.be` (`load("vault.bec")`), `vault.bec` (bytecode), `vault/device.id` (16 B), `vault/keyring.bin` (108 B), `vault/sealed.bin` (74 B).
   - `keyring.bin` = 3 entries `epoch(u32 LE) ‖ key 32 B` → **epochs 6, 7, 8**.
3. **Decompile `vault.bec`.** No `berry` binary available → in-house disassembler (`work/bec_dis.py`) based on `be_bytecode.c` (format) + `be_opcodes.h`/`be_decoder.h` (opcodes, fields OP@26/6, RA@18/8, RKB@9/9, RKC@0/9, bit 8 = constant). Reveals the `unseal` function:
   ```
   aes_key = HMAC_SHA256(key = keyring[epoch],
             msg = b"tasmota-vault/unwrap/v2" + b"\x00" + device_id(16)
                   + epoch(4 LE) + nonce(32))            # 32 B
   sealed.bin = IV(12) ‖ ciphertext(46) ‖ tag(16)
   plaintext  = AES_256_GCM(aes_key, IV=sealed[0:12]).decrypt(ciphertext)   # no AAD
   # then check: calculated tag == sealed[-16:] (otherwise “authentication tag”)
   ```
Guards: `device` == device.id, nonce 32 B, epoch ≥ 1, keyring multiple of 36, `duplicate epoch`.
4. **Find epoch/nonce.** `mqtt.pcap` → PUBLISH on `farm/gw-01/cmnd/VaultRotate`:
   - epoch **7**, nonce `9bb1ebe2…65f0` (**retain=1**, history);
   - epoch **8**, nonce `1a3dfb13…2606` (live).
5. **Decrypt + check tag** (`work/solve.py`): epoch 7 → tag **FAIL** (decoy); epoch **8** → **tag OK** → `hiCTF{b3rry_r0t4t10n_c94934d76344ab1151e03afd}`.

2. **Key concept**

Extracting a **LittleFS partition** from an ESP32 flash image, **decompiling the Berry v4 bytecode** (custom agent) to reconstruct the KDF, then decrypting **AES-256-GCM** of the sealed record with the correct **epoch/nonce** found in the MQTT traffic (the valid GCM tag).

3. **Flaws / to remember**

- Security is based on the secret of the flash keyring: which reads the flash **replays** any rotation captured. The authenticable record = the one whose (epoch, nonce) **matches the GCM tag**.
- **No brute force**: the AES-GCM tag is an oracle of validity → we test the observed rotations and only one authenticates.
- **Pitfalls**: misleading partition label (spiffs → LittleFS); message retained (epoch 7) which resembles the current state but is a decoy; `tele/STATE` = noise.
- `bytes().add(n, 4)` = little-endian integer on 4 B; `bytes("00")` = parsing **hex** → `\x00`; `bytes().fromstring(s)` = raw bytes of the string; `bytes.get(off, 4)` = u32 LE.
- Recognize this type: flash image of an IoT device + network capture ⇒ extract the FS, decompile the agent (Berry/Lua/…), replay/validate with the traffic.

## Solve script
Script path: [scripts/bec_dis.py](scripts/bec_dis.py)
Script path: [scripts/solve.py](scripts/solve.py)

## Flag
hiCTF{b3rry_r0t4t10n_c94934d76344ab1151e03afd}

## Lessons and reusable patterns
- Main technique: pcap-analysis.
