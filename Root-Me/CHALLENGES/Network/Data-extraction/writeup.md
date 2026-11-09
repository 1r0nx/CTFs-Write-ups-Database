---
title: "Data-extraction"
ctf: "Root-Me"
category: "network"
difficulty: "medium"
points: 20
techniques: ["pcap-analysis", "smb", "nfs", "ftp"]
tools: ["wireshark", "tshark", "tar", "python"]
keywords: ["Data-extraction", "Root-Me", "network", "pcap-analysis", "smb", "nfs", "ftp", "wireshark", "tshark", "tar", "python", "pcap", "pcapng", "png", "jpg", "tcp"]
status: "solved"
has_script: true
source: "Root-Me/Network/Data-extraction/note.md"
---

# Data extraction (Root-Me, network)

## Summary
Challenge **Data-extraction** from the Root-Me CTF, network category. Main technique: pcap-analysis. Source file: chall_wireshark.pcapng — a capture where files pass through three different protocols: FTP, SMB and NFS. Objective: extract everything, the flag is hidden in one of the recovered files.

## Statement and artefacts

**Official statement (Root-Me, English page):**

Your network teacher provides you with this capture and asks you to try and find the files he has sent through your test lab.

The flag is the concatenation of the three flags present in the files.

Good luck! :)

**sha256sum:** `66adb6a6a6c96c486e9f1856bf5039ab3b7a713b2a94e834ed281e7444f8aea7`

- **Category:** Network
- **Difficulty:** Medium
- **Points:** 20
- **Author(s):** Tidusrose
- **Published:** 2024-05-28 12:00:41
- **Root-Me page:** https://www.root-me.org/en/Challenges/Network/Data-extraction

**Provided file (as listed on Root-Me):**
- [`ch31.zip`](https://static.root-me.org/reseau/ch31/ch31.zip) — challenge archive.

## Recognition signals
- Signal: File carving from multi-protocol network capture.
- Signal: Each protocol is recovered differently: some are managed natively by Wireshark/tshark, others (NFS) require manual reassembly.

## Resolution method
1. **FTP -> tshark**

Files pass through **FTP-DATA** connections (channel separate from command channel). We reconstruct each data flow to recover the file. Files obtained: `cat.jpg`, `cat2.png`, `cookie.txt` (folder `ftp/`). The names keep the server path (`/home/tidusrose/FTP/...`, `/` encoded as `%2f`).

2. **SMB -> tshark (export objects)**

SMB is managed natively: `tshark -r chall_wireshark.pcapng --export-objects smb, smb/` → `books.pdf`, `congradulation.odt`, `maybe.tar.gz` (folder `smb/`). The names keep the `\` SMB encoded as `%5c`.

3. **Key concept**

**Extracting files (file carving) from a multi-protocol network capture.** Each protocol is retrieved differently: some are managed natively by Wireshark/tshark, others (NFS) require manual reassembly.

## Solve script
Script path: [scripts/nfs-extract.py](scripts/nfs-extract.py)

## Flag
Zeld@P0kemonM@rio

## Lessons and reusable patterns
- Reflex “files in a pcap”: first tshark --export-objects <proto>,<dir>
- NFS is not supported by export-objects -> manual reassembly of READs
- Recognize this type: a single capture, several transfer protocols
- Encoded filenames (%2f=/, %5c=\) = original paths, normal.
