---
title: "Packets-lo_l"
ctf: "Pwny-CTF"
category: "network"
difficulty: "hard"
points: 0
techniques: ["aes-cbc", "pcap-analysis", "icmp-exfiltration", "encoding"]
tools: ["strings", "xxd", "zsteg", "tshark", "openssl", "unzip", "pycryptodome", "python"]
keywords: ["Packets-lo_l", "Pwny-CTF", "network", "aes-cbc", "pcap-analysis", "icmp-exfiltration", "encoding", "strings", "xxd", "zsteg", "tshark", "openssl", "unzip", "pycryptodome", "python", "pcap"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Networking/Packets-lo_l/notes.md"
---

# Packets-lo_l (Pwny-CTF, network)

## Summary
Challenge **Packets-lo_l** from the Pwny-CTF CTF, network category. Main technique: aes-cbc. Loopback (lo, 127.0.0.1) often captures duplicate packets -> deduplicate before reconstructing data.

## Statement and artefacts
Sombra hacked my computer and left a message. Can you help me figure out what it said?

**Author**: Dillon

**Provided files / artifacts:**
- `sombra_hacks_packs.pcap (network capture, 67.2 KB)`
- `work/cipher.bin (binary/data, 19.9 KB)`
- `work/message.b64 (file, 19.9 KB)`
- `work/message.docx (document, 14.7 KB)`
- `work/udp_cipher.bin (binary/data, 39.9 KB)`

## Recognition signals
Not specified.

## Resolution method
1. **Protocol hierarchy** — `tshark -r sombra_hacks_packs.pcap -q -z io, phs` → only **UDP** and **ICMP**, all on `127.0.0.1` (loopback → pun “lo_l”).
2. **Read ICMP channel in text** — `tshark... -Y 'icmp' -T fields -e data.data | tr -d '\n' | xxd -r -p | strings` → reveals `awesomesecretkey`, `awesomesecretiv!`, `oops ignore that lol` in plain text.
3. **Free hint (0 pt)**: *“The UDP bytes are encrypted”*.
4. **Understand the structure** — each message is sent in **double** (UDP + ICMP mirroring, loopback artifact). Sequence: `key` → `IV` → `decoy` → pieces of **ciphertext**.
5. **Reconstruct the ciphertext** (`solve.py`) from ICMP (duplicates, throw away the 3 markers) → 20384 bytes, multiple of 16. ✅
6. **Decrypt AES-128-CBC** — `pycryptodome` absent → `openssl enc -d -aes-128-cbc -K <hex_key> -iv <iv_hex> -in cipher.bin` → comes out of **base64** (`UEsDBB…` = ZIP `PK`).
7. **Unpack** — `base64 -d` → file `.docx` (= ZIP); `unzip` → `word/media/image1.png`.
8. **Read the image** → the flag is **handwritten**: `flag{b33n_h3r3_all_al0ng}`.

1. **More difficult variation**

- Key/IV **not provided** in the capture → they would have to be brute-forced or deduced (weak password + KDF).
- Ciphertext **fragmented and mixed** with legitimate traffic → filter more finely (port `31337`, etc.).
- Last layer: image with the flag in **steganography** (zsteg/LSB) rather than written in plain text.

## Solve script
Script path: [scripts/solve.py](scripts/solve.py)

## Flag
flag{b33n_h3r3_all_al0ng}

## Lessons and reusable patterns
- Loopback (lo, 127.0.0.1) often captures duplicate packets -> deduplicate before reconstructing data.
- The same message can be broadcast over several protocols (here UDP and ICMP): choosing one is enough. ICMP can carry arbitrary data (here type 3).
- Recognize layers by their magic bytes / prefixes: UEsDBB (base64) = PK = ZIP; a.docx/.xlsx/.pptx is a ZIP -> unzip to search (word/media/ for images).
- Key + IV of 16 bytes = AES-128; presence of an IV = CBC mode. The ciphertext must be a multiple of 16.
- openssl enc -d -aes-128-cbc -K <hex> -iv <hex> decrypts without Python dependency (key/IV in hexadecimal).
