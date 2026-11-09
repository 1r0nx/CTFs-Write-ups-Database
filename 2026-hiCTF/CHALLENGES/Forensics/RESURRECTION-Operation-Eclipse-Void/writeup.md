---
title: "RESURRECTION-Operation-Eclipse-Void"
ctf: "2026-hiCTF"
category: "forensics"
difficulty: "hard"
points: null
techniques: ["xor-cipher", "substitution-cipher", "disk-forensics", "log-analysis", "encoding"]
tools: ["sleuthkit", "python"]
keywords: ["RESURRECTION-Operation-Eclipse-Void", "hiCTF", "forensics", "xor-cipher", "substitution-cipher", "disk-forensics", "log-analysis", "encoding", "sleuthkit", "python", "pe", "zip", "xor", "base64", "hex"]
status: "solved"
has_script: true
source: "hiCTF/Forensics/RESURRECTION-Operation-Eclipse-Void/notes.md"
---

# RESURRECTION-Operation-Eclipse-Void (hiCTF, forensics)

## Summary
Challenge **RESURRECTION-Operation-Eclipse-Void** from the hiCTF CTF, forensics category. Main technique: xor-cipher. “Shattered-Geometry, Chrono-Echoes, and Unmapped-Voids”; 5 segments, each with an ordinal label, to concatenate.

## Statement and artefacts
“Shattered-Geometry, Chrono-Echoes, and Unmapped-Voids”; 5 segments, each with an ordinal label, to concatenate.

**Provided files / artifacts:**
- `resurrection.zip (archive, 3.2 MB)`

## Recognition signals
- Signal: data hidden in the filesystem structure (geometry, metadata, timestamps, $Bitmap), not in files.
- Signal: Compare structures that should match: $Bitmap vs runlists, $MFT vs $MFTMirr, $SI vs $FN, stored vs recalculated CRCs.
- If we look at zsh trap, thinking of a variable named path overwrites PATH.

## Resolution method
1. **Step 0 — repair geometry**

| Constat | Order / read | Result |
|---|---|---|
| MBR, primary GPT, NTFS boot sector **to zero** | map of non-zero zones (4 KiB blocks) | Recognizable NTFS (`FILE0`, `INDX`, `RSTR`) |
| GPT **backup** intact | `EFI PART` to 0x3FFFFE00, entries at LBA 2097119 | “Basic data” partition LBA 32768 → 2093055 |
| Boot sector **emergency** | last sector of the partition (0x3FDFFE00) | 4 KiB clusters, `$MFT` cluster 85845 |
| Repair (on the copy) | `dd if=img of=img bs=512 skip=2093055 seek=32768 count=1 conv=notrunc` | `fsstat`/`fls -o 32768` work |

2. **The 5 segments**

| # | Label | Or | Technique | Payload |
|---|---|---|---|---|
| 1 | `f!r5t` | `Windows/System32/kbdusx.dll` (MFT 179) | **Overlay PE** (44 B after the section) XORed with the **TimeDateStamp** (`80 85 EC 65`) | `hiCTF{p3_0v3rl4y_71m3d473574mp_k3y_` |
| 2 | `53c0nd` | stream `$DATA` of **folder** `Confidential_Q3` (MFT 111) | **Lengths of the 34 fragments** of the runlist = ASCII (zero content) | `n7f5_runl157_cl5_g30m37ry_` |
| 3 | `th1jd` | `config/TxR/tx_journal.log` (MFT 181) | **Differences between consecutive timestamps** − 9984 = ASCII | `7r4ns4c710n_n4n0_f1l371m3_` |
| 4 | `f0\|_\|rth` | `winevt/Logs/Security_Audit.evtx` (MFT 193) | 33 **BinXML substitution values** UInt32 = 1 character each | `3v7x_b1n4ry_xml_70k3n5_` |
| 5 | `5\|f7h` | `$Bitmap` | 40 clusters **allocated without owner**; **gaps** between them = ASCII | `b17m4p_orph4n_v01d_r35urr3c710n}` |

Clues that guided:
- Seg. 1: `kbdusx.dll` has an **inconsistent timestamp** (modified before being created = timestomping) and the PowerShell history reports "*anomalous unsigned input filter driver … kbdusx.dll*".
- Seg. 2: a **folder** with a very fragmented `$DATA` of 11 MB.
- Seg. 3/4: measurement of **entropy** of files → almost all random (decoys), only `tx_journal.log`, `Security_Audit.evtx` structured.
- Seg. 5: comparison **`$Bitmap` ↔ actually used clusters** (`istat` of all inodes).
- The label of the seg. 3 reads `th1jd` (a value shifted by 8, probably a typo): without effect, only the part after `--` counts.

## Discarded approaches
- ASCII/UTF-16, Base64/hex strings: nothing (everything is structural).
- Unallocated (blkls): empty. Slack MFT and INDX: ordinary NTFS remains. $LogFile: normal logs. $MFTMirr = $MFT.
- CRC of GPT entries = 0xDEADBEEF: “broken” geometry index, not a key (XOR tested).
- Zero flow of Confidential_Q3, $BadClus:$Bad: empty.

## Solve script
Script path: [scripts/solve.py](scripts/solve.py)

## Flag
hiCTF{p3_0v3rl4y_71m3d473574mp_k3y_n7f5_runl157_cl5_g30m37ry_7r4ns4c710n_n4n0_f1l371m3_3v7x_b1n4ry_xml_70k3n5_b17m4p_orph4n_v01d_r35urr3c710n}

## Lessons and reusable patterns
- Recognize: “zero files”, “support structure” -> search in metadata: runlists, $Bitmap, timestamps, GPT/boot sector, overlays, BinXML.
- Destroyed geometry: NTFS has a backup boot sector (last sector of the volume), GPT a copy at the end of the disk.
- Compare structures that should match: $Bitmap vs runlists, $MFT vs $MFTMirr, $SI vs $FN, stored vs recalculated CRCs.
- Data in deviations / lengths (not in values): think of chr(difference).
- zsh trap: a variable named path overwrites PATH.
