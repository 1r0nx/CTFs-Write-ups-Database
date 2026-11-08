---
title: "Pool-1"
ctf: "Pwny-CTF"
category: "network"
difficulty: "Not specified"
points: 100
techniques: ["pcap-analysis", "smb"]
tools: ["tshark"]
keywords: ["Pool-1", "Pwny-CTF", "network", "pcap-analysis", "smb", "tshark", "pcap"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Networking/Pool-1/notes.md"
---

# Pool-1 (Pwny-CTF, network)

## Summary
Challenge **Pool-1** from the Pwny-CTF CTF, network category. Main technique: pcap-analysis. NetBIOS Name Service (NBNS) announces the names of Windows machines; suffix <00>/<20> = type of service.

## Statement and artefacts
Layer 5 represents the session layer of the OSI model, which includes protocols like NetBIOS and SMB.

The flag is the NetBIOS name (in uppercase) of the Windows PC, e.g. `sigpwny{DESKTOP-ABCD123}`.

**Author**: Minh

**Provided files / artifacts:**
- `pool.pcap (network capture, 9.5 MB)`

## Recognition signals
Not specified.

## Resolution method
1. The flag = the NetBIOS name (in ALL CAPS) of the Windows PC, in `pool.pcap`.
2. `tshark -r pool.pcap -Y 'nbns' -T fields -e nbns.name` (or look at Browser/SMB) → `EIGHTBALL<00>` (Workstation), `EIGHTBALL<20>` (Server).
3. Flag = `sigpwny{EIGHTBALL}` (checked).

## Flag
sigpwny{EIGHTBALL}

## Lessons and reusable patterns
- NetBIOS Name Service (NBNS) announces the names of Windows machines; suffix <00>/<20> = type of service.
- Useful filters: nbns, browser, smb/smb2.
