---
title: "Layer-3"
ctf: "Pwny-CTF"
category: "network"
difficulty: "Not specified"
points: 50
techniques: ["pcap-analysis", "dns"]
tools: ["wireshark", "tshark"]
keywords: ["Layer-3", "Pwny-CTF", "network", "pcap-analysis", "dns", "wireshark", "tshark", "pcap", "http"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Networking/Layer-3/notes.md"
---

# Layer-3 (Pwny-CTF, network)

## Summary
Challenge **Layer-3** from the Pwny-CTF CTF, network category. Main technique: pcap-analysis. Associate a host (HTTP Host / DNS) with its destination IP (layer 3).

## Statement and artefacts
Use Wireshark to open `layers.pcap` and complete the challenge. The file is the same from `Layer 1`.

Layer 3 represents the network layer of the OSI model, which includes the Internet Protocol (IP) and packet routing.

The flag is the IP address of the web server running the NFT gallery (e.g. `sigpwny{192.168.0.1}`).

**Author**: Minh

## Recognition signals
Not specified.

## Resolution method
1. The flag = the **IP** of the web server hosting the NFT gallery.
2. `tshark -r layers.pcap -Y 'http.request' -T fields -e ip.dst -e http.host | grep nftgallery` → `192.168.56.128 nftgallery.local`.
3. Flag = `sigpwny{192.168.56.128}` (checked).

## Flag
sigpwny{192.168.56.128}

## Lessons and reusable patterns
- Associate a host (HTTP Host / DNS) with its destination IP (layer 3).
- http.request filter + ip.dst/http.host fields.
