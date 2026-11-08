---
title: "Hall-of-Mirrors"
ctf: "2026-hiCTF"
category: "stego"
difficulty: "Not specified"
points: null
techniques: ["xor-cipher", "prng-mt19937", "elliptic-curve", "audio-steganography", "reverse-engineering", "vm-reverse"]
tools: ["unzip", "python"]
keywords: ["Hall-of-Mirrors", "hiCTF", "stego", "xor-cipher", "prng-mt19937", "elliptic-curve", "audio-steganography", "reverse-engineering", "vm-reverse", "unzip", "python", "zip", "ecc", "xor", "prng", "lattice"]
status: "solved"
has_script: true
source: "hiCTF/steg/Hall-of-Mirrors/notes.md"
---

# Hall-of-Mirrors (hiCTF, stego)

## Summary
Challenge **Hall-of-Mirrors** from the hiCTF CTF, stego category. Main technique: xor-cipher. 3-layer chain (“hall of mirrors”): each layer links to the next, two hiCTF{} are decoys, only one “exit”. The index archivist-datasheet.zip gives all the technical specifications.

## Statement and artefacts
3-layer chain (“hall of mirrors”): each layer links to the next, two hiCTF{} are decoys, only one “exit”. The index archivist-datasheet.zip gives all the technical specifications.

**Provided files / artifacts:**
- `archivist-datasheet.zip (archive, 1.7 KB)`
- `hall-of-mirrors.zip (archive, 285.6 MB)`
- `work/hall-of-mirrors.wav (audio, 285.6 MB)`
- `work/notes.npy (file, 105.8 KB)`
- `work/payload.bin (binary/data, 6.1 KB)`
- `work/vm_out.bin (binary/data, 5.0 KB)`

## Recognition signals
- Signal: A datasheet/index that specifies everything = “pipeline” challenge: we implement faithfully, we don’t guess.
- If we look at PRNG which plans positions (not a stupid LSB), think of “jumping” stego; the CRC in the frame confirms the key.
- Signal: Home VM + hash by fetch + instr which decrypts code = anti-disassembly: emulate as is, do not patch anything.
- Signal: secp256k1 + lots of signatures + small parameter L = biased nonces -> LLL/HNP. Number of.
- Signal: Decoys: hiCTF{just_lsb_n0ise} (in raw LSBs) and hiCTF{stop_here} (written hard in the.
- Signal: Non-uniform ECDSA nonces (12 bits high at 0) = leak exploitable by Euclidean network -> private key.

## Resolution method
1. **Overview**

WAV 48 kHz stereo 16-bit, 26 min. Three floors, described in `work/hint/archivist_datasheet.txt`:
1. **MirrorStego v1**: hidden bits in the low byte of samples, planning by SplitMix64(K).
2. **MVM1**: the extracted payload is the image of a 16-bit self-decrypting VM → new TLV.
3. **ECC unsealing**: TLV = secp256k1 curve + 48 ECDSA signatures with **truncated nonces** → LLL/HNP recovers the private key `d` → KDF(d) → stream encryption → flag.

2. **Method (step -> command -> what it reveals)**

| # | Stage | Command | Revealed |
|---|---|---|---|
| 0 | Spectral panel (already done) | `demod.py` | `K=9C4F1E7A3B50D682`, name `MIRRORS1` |
| 1 | Read the clue | `unzip archivist-datasheet.zip` | the spec of the 3 floors |
| 2 | Extract bits | `extract_frame.py wav K payload.bin` | `MIRRORS1`+len+crc, **CRC32 OK** (6266 B) |
| 3 | Run the VM | `mvm1.py payload.bin vm_out.bin` | HLT, 5083 B = new TLV `MIRRORS1` |
| 4 | Parse the TLV | `parse_tlv.py vm_out.bin` | secp256k1, Q, L=12, 48 triples, sealed blob 33 B |
| 5 | LLL + unsealing | `solve_hnp.py vm_out.bin` | `d`, key32, **flag** |

3. **Detail of the 3 floors**

- **Stage 1 — scheduled stegano.** SplitMix64 initialized with K (the `K=` of the spectral panel). From `p=-1`, **2 draws per bit**: draw 1 → not `p += 1 + (r%4096)` (jumps forward, hence “reflections pointing at one another”), draw 2 → mask `w=(r>>17)&0xFF`. Bit = `popcount(low_byte(S[p]) ^ w) & 1`, set **MSB-first**. Frame: `MIRRORS1 | len(u32 LE) | crc32(u32 LE) | payload`. Valid CRC = good K.
- **Floor 2 — VM MVM1.** Image `MVM1 | code_len | data_len | entry | rsv`. Register `R15` = FNV-like hash updated **on each fetch**; the `SMC` instruction decrypts a CODE area with a seed `R[rs]^R15` (xorshift64): **anti-trace self-decryption** (if you skip/alter an instr, R15 diverges and the code decodes into mush). Faithful emulation → re-issues a `MIRRORS1` TLV.
- **Stage 3 — HNP (Hidden Number Problem).** TLV: secp256k1 (n, p, a=0, b=7, G), public key `Q`, `L=12`, 48 triples `(h, r, s)` (ECDSA), sealed blob. The nonces are **truncated**: 12 most significant zero bits, therefore `k < 2^244`. With `k = s⁻¹h + s⁻¹r·d (mod n)` small, we set up a **network** (lattice) and **LLL** outputs `d`. Unambiguous check: `d·G == Q`. Then `KDF(d)` → 32 B of key, **stream encryption** (ARX mix ChaCha type) → XOR on the blob → ASCII flag (33 B = size of the blob).

4. **To remember (recognize this type)**

- **A datasheet/index that specifies everything** = “pipeline” challenge: we implement faithfully, we don’t guess.
- **PRNG which plans positions** (not a stupid LSB) → “jumping” stego; the CRC in the frame confirms the key.
- **Homemade VM + hash by fetch + instr which decrypts code** = anti-disassembly: emulate as is, do not patch anything.
- **secp256k1 + lots of signatures + small parameter `L`** = biased nonces → **LLL/HNP**. Number of sigs ≈ 256/L (here 48 for 12 bits: wide margin). Success criterion = `d·G == Q`, not “it looks like”.
- **Decoys**: `hiCTF{just_lsb_n0ise}` (in raw LSBs) and `hiCTF{stop_here}` (written hard in the VM program, “flag is … no further steps required” = lie). Always go to the end of the chain.

5. **Flaws / key points in the source code (datasheet)**

- Non-uniform ECDSA nonces (12 bits high at 0) = **exploitable leak** by Euclidean network → private key.
- VM self-decryption depends on the integrity of the execution flow (R15), not on an external secret: emulable.

## Solve script
Script path: `scripts/analyze_tuples.py`
Script path: `scripts/cepstrum.py`
Script path: `scripts/demod.py`
Script path: `scripts/extract_frame.py`
Script path: `scripts/global_ac.py`
Script path: `scripts/lsb_hunt.py`
Script path: `scripts/mirror_dup.py`
Script path: `scripts/mvm1.py`
Script path: `scripts/notes_detect.py`
Script path: `scripts/parity_coding.py`
Script path: `scripts/parse_tlv.py`
Script path: `scripts/sm64.py`
Script path: `scripts/sm64_anystart.py`
Script path: `scripts/sm64_bit1.py`
Script path: `scripts/sm64_block.py`
Script path: `scripts/sm64_lemire.py`
Script path: `scripts/sm64_magic.py`
Script path: `scripts/sm64_modG.py`
Script path: `scripts/sm64_modG2.py`
Script path: `scripts/sm64_scan.py`
Script path: `scripts/sm64_wide.py`
Script path: `scripts/solve_hnp.py`
Script path: `scripts/tonal_scan.py`

## Flag
hiCTF{h1dd3n_numb3r_l4ttice_le4k}

## Lessons and reusable patterns
- Main technique: xor-cipher.
