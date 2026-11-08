---
title: "The-Quiet-Divide"
ctf: "2026-hiCTF"
category: "network"
difficulty: "Not specified"
points: null
techniques: ["path-traversal", "pcap-analysis", "firmware-analysis", "git-forensics"]
tools: ["wireshark", "python"]
keywords: ["The-Quiet-Divide", "hiCTF", "network", "path-traversal", "pcap-analysis", "firmware-analysis", "git-forensics", "wireshark", "python", "http", "firmware", "sqlite"]
status: "solved"
has_script: true
source: "hiCTF/network/The-Quiet-Divide/notes.md"
---

# The-Quiet-Divide (hiCTF, network)

## Summary
Challenge **The-Quiet-Divide** from the hiCTF CTF, network category. Main technique: path-traversal. Challenge in duplicate. Full notes (model, crypto chain, traps) are in../../Forensics/The-Quiet-Divide/notes.md. Summary of the unlock: The deployed firmware 0835dfce (essential for evidence -> archive_key) is not on /v3/dist (which only serves the qualified firmware 7f2081d3).

## Statement and artefacts
Challenge in duplicate. Full notes (model, crypto chain, traps) are in../../Forensics/The-Quiet-Divide/notes.md. Unlock summary:

The deployed firmware 0835dfce (essential for evidence -> archive_key) is not on /v3/dist (which only serves the qualified firmware 7f2081d3). It is served by a second distribution service 10.77.40.35:8085 — which Wireshark wrongly dissects into the woww (World of Warcraft) protocol, making it invisible to http filters. Reassembled by Range -> sha256 0835dfce ✓. Then: evidence (custody 5 events full form + firmware 0835 + sigs attestation/observation + codec) -> archive_key -> decryption of the 3 AVLT10 ops-17 -> SQLite -> authoritative transaction (case_commit=b34dc728 + release_checkpoint=5e4f78ad, tx 6dd9ec58) -> material -> final_key -> decrypt_seal -> flag.

**Provided files / artifacts:**
- `the-quiet-divide.zip (archive, 139.4 MB)`
- `work/FLAG-trouve.txt (text, 48 B)`
- `work/firmware_0835.bin (binary/data, 14.2 KB)`

## Recognition signals
Not specified.

## Resolution method
1. **Flag: `hiCTF{c8c46fdbd6e5e4eacabfba53a156ff9ab10567f2}`**

2. Challenge in duplicate. The **full notes** (model, crypto chain, traps) are in `../../Forensics/The-Quiet-Divide/notes.md`. Unlock summary:

3. The **deployed** firmware `0835dfce` (essential for `evidence → archive_key`) is not on `/v3/dist` (which only serves the *qualified* firmware `7f2081d3`). It is served by a **second distribution service** `10.77.40.35:8085` — which **Wireshark wrongly dissects into `woww` (World of Warcraft) protocol**, making it invisible to `http` filters. Reassembled by Range → sha256 `0835dfce` ✓.

4. Then: evidence (custody 5 events full form + firmware 0835 + sigs attestation/observation + codec) → `archive_key` → decryption of the 3 AVLT10 **ops-17** → SQLite → authoritative transaction (`case_commit=b34dc728` + `release_checkpoint=5e4f78ad`, tx `6dd9ec58`) → `material` → `final_key` → `decrypt_seal` → flag.

5. Scripts: `work/extract_fw0835.py`, `work/decrypt_all.py`, `work/final_solve.py`, `work/firmware_0835.bin`.

## Solve script
Script path: `scripts/decrypt_all.py`
Script path: `scripts/extract_fw0835.py`
Script path: `scripts/final_solve.py`

## Flag
hiCTF{c8c46fdbd6e5e4eacabfba53a156ff9ab10567f2}

## Lessons and reusable patterns
- Main technique: path-traversal.
