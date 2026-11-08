---
title: "Layer-2"
ctf: "Pwny-CTF"
category: "network"
difficulty: "Not specified"
points: 30
techniques: ["pcap-analysis"]
tools: ["wireshark", "tshark"]
keywords: ["Layer-2", "Pwny-CTF", "network", "pcap-analysis", "wireshark", "tshark", "pcap"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Networking/Layer-2/notes.md"
---

# Layer-2 (Pwny-CTF, network)

## Summary
Challenge **Layer-2** from the Pwny-CTF CTF, network category. Main technique: pcap-analysis. ARP resolves an IP to a MAC address. Arp filter in Wireshark; fields eth.src/eth.dst, arp.src/dst.proto_ipv4.

## Statement and artefacts
Use Wireshark to open `layers.pcap` and complete the challenge. The file is the same from `Layer 1`.

Layer 2 represents the data link layer of the OSI model, which includes things like packet frames and MAC addresses.

The flag is the MAC address that was requested by packet number 16 through ARP (e.g. `sigpwny{a8:9e:Ac:b3:18:01}`).

**Author**: Minh

## Recognition signals
Not specified.

## Resolution method
1. The flag = the MAC targeted by frame **16** (an **ARP** request) from `layers.pcap`.
2. `tshark -r layers.pcap -Y "frame.number==16" -T fields -e eth.dst -e eth.src -e arp.opcode` → `eth.dst = 00:50:56:ea:b5:f8` (opcode 1 = request).
3. Flag = `sigpwny{00:50:56:ea:b5:f8}` (checked).

## Flag
sigpwny{00:50:56:ea:b5:f8}

## Lessons and reusable patterns
- ARP resolves an IP to a MAC address. Arp filter in Wireshark; fields eth.src/eth.dst, arp.src/dst.proto_ipv4.
- MAC address = Layer 2 hardware identifier (6 bytes).
