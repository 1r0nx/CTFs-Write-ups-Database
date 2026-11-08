---
title: "Layer-1"
ctf: "Pwny-CTF"
category: "network"
difficulty: "Not specified"
points: 30
techniques: ["pcap-analysis", "encoding"]
tools: ["wireshark", "tshark"]
keywords: ["Layer-1", "Pwny-CTF", "network", "pcap-analysis", "encoding", "wireshark", "tshark", "pcap", "hex"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Networking/Layer-1/notes.md"
---

# Layer-1 (Pwny-CTF, network)

## Summary
Challenge **Layer-1** from the Pwny-CTF CTF, network category. Main technique: pcap-analysis. “Hex stream” of a packet = all its bytes (including Ethernet header). In Wireshark: Copy -> as a Hex Stream.

## Statement and artefacts
Use Wireshark to open `layers.pcap` and complete the challenge.

Layer 1 represents the physical layer of the OSI model, which includes things like cables to transfer data or simply binary.

The flag is the complete hex stream of packet number 16 (e.g. `sigpwny{005056e9e5...776f726c64}`).

**Author**: Minh

**Provided files / artifacts:**
- `layers.pcap (network capture, 4.9 MB)`

## Recognition signals
Not specified.

## Resolution method
1. The flag = the **complete hexadecimal stream of frame n°16** of `layers.pcap`.
2. `tshark -r layers.pcap -Y "frame.number==16" -x` (hex dump), or in Wireshark: right click on the packet → Copy → …as Hex Stream.
3. Concatenate bytes → `sigpwny{005056eab5f8...0000}` (verified: same as flag.txt).

## Flag
sigpwny{005056eab5f8000c299a900d08060001080006040001000c299a900dc0a83880000000000000c0a838fe000000000000000000000000000000000000}

## Lessons and reusable patterns
- “Hex stream” of a packet = all its bytes (including Ethernet header). In Wireshark: Copy -> as a Hex Stream.
- Frame 16 here is an ARP request (see Layer 2).
