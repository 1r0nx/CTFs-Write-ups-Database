---
title: "Baby-Wireshark-Doo-Doo-Doo"
ctf: "Pwny-CTF"
category: "network"
difficulty: "Not specified"
points: 100
techniques: ["pcap-analysis", "encoding"]
tools: ["wireshark", "tshark", "php"]
keywords: ["Baby-Wireshark-Doo-Doo-Doo", "Pwny-CTF", "network", "pcap-analysis", "encoding", "wireshark", "tshark", "php", "pcap", "http", "base64", "got"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Networking/Baby-Wireshark-Doo-Doo-Doo/notes.md"
---

# Baby-Wireshark-Doo-Doo-Doo (Pwny-CTF, network)

## Summary
Challenge **Baby-Wireshark-Doo-Doo-Doo** from the Pwny-CTF CTF, network category. Main technique: pcap-analysis. pcap HTTP reflex: export the objects to find transferred pages/files, then search their content.

## Statement and artefacts
Help, we got pwned and I'm supposed to find the hacker's secret in this network traffic. I heard Wireshark might be useful here.

Flag format: `flag{...}`

**Author**: Jesse

**Provided files / artifacts:**
- `challenge.pcap (network capture, 17.3 MB)`

## Recognition signals
Not specified.

## Resolution method
1. Open the capture and **export the HTTP objects** (Wireshark: *File → Export Objects → HTTP*; or `tshark -r cap.pcap --export-objects http, extracted/`) → `extracted/` folder with the transferred files, including a `index.php`.
2. Read the page — `cat extracted/index.php` → contains a **base64** string (`ZmxhZ3tIYW1tMG5kXzFzX0F3M3MwbTN9`).
3. Decode — `echo "ZmxhZ3tIYW1tMG5kXzFzX0F3M3MwbTN9" | base64 -d` → `flag{Hamm0nd_1s_Aw3s0m3}`.

## Solve script
Script path: [scripts/index.php](scripts/index.php)

## Flag
flag{Hamm0nd_1s_Aw3s0m3}

## Lessons and reusable patterns
- pcap HTTP reflex: export the objects to find transferred pages/files, then search their content.
- An alphanumeric string in A-Za-z0-9+/ (often ending with =) = base64 -> base64 -d.
