---
title: "Layer-4"
ctf: "Pwny-CTF"
category: "network"
difficulty: "Not specified"
points: 50
techniques: ["pcap-analysis", "dns", "icmp-exfiltration"]
tools: ["wireshark", "tshark"]
keywords: ["Layer-4", "Pwny-CTF", "network", "pcap-analysis", "dns", "icmp-exfiltration", "wireshark", "tshark", "pcap", "icmp", "tcp", "http"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Networking/Layer-4/notes.md"
---

# Layer-4 (Pwny-CTF, network)

## Summary
Challenge **Layer-4** from the Pwny-CTF CTF, network category. Main technique: pcap-analysis. Tshark = command line version of Wireshark. Key options:

## Statement and artefacts
Use Wireshark to open `layers.pcap` and complete the challenge. The file is the same from `Layer 1`.

Layer 4 represents the transport layer of the OSI model, which includes things like TCP, UDP, ICMP, and port numbers.

The flag is the TCP port number where the last RST packet was sent to (e.g. `sigpwny{80}`).

**Author**: Minh

## Recognition signals
- Signal: tail -1 to keep only the last occurrence when several packets match.
- Signal: Trap: -Y (display filter) ≠ -f (BPF capture filter, different syntax).

## Resolution method
1. Open the capture and keep only TCP packets with the **RST** flag (reset) — `tshark -r../layers.pcap -Y 'tcp.flags.reset==1' -T fields -e frame.number -e frame.time -e ip.src -e ip.dst -e tcp.srcport -e tcp.dstport | tail -1`
2. The last RST packet gives the desired port → flag `sigpwny{38432}`.

## Flag
sigpwny{38432}

## Lessons and reusable patterns
- tshark = command line version of Wireshark. Key options:
- -r <file.pcap>: read a capture.
- -Y '<filtre>': Wireshark display filter (e.g. tcp.flags.reset==1, http, dns).
- -T fields -e <field>: output in columns, one -e per desired field (ip.src, tcp.dstport, etc.).
- TCP RST flag: signals a sudden connection cutoff (port closed/refused). Each “layer” in this series of challenges targets a different TCP/IP flag or property -> learn the associated Wireshark filters.
- tail -1 to keep only the last occurrence when several packets match.
- Trap: -Y (display filter) ≠ -f (BPF capture filter, different syntax).
