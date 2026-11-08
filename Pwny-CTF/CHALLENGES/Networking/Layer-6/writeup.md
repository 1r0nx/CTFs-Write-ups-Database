---
title: "Layer-6"
ctf: "Pwny-CTF"
category: "network"
difficulty: "Not specified"
points: 75
techniques: ["pcap-analysis", "encoding"]
tools: ["wireshark", "tshark"]
keywords: ["Layer-6", "Pwny-CTF", "network", "pcap-analysis", "encoding", "wireshark", "tshark", "pcap", "png", "jpeg", "http"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Networking/Layer-6/notes.md"
---

# Layer-6 (Pwny-CTF, network)

## Summary
Challenge **Layer-6** from the Pwny-CTF CTF, network category. Main technique: pcap-analysis. Export of HTTP objects: recovers all transferred files (images, pages, etc.) from a capture at once.

## Statement and artefacts
Use Wireshark to open `layers.pcap` and complete the challenge. The file is the same from `Layer 1`.

Layer 6 represents the presentation layer of the OSI model, which represents how data is encoded or encrypted, such as the JPEG image format or TLS encryption.

The flag is in one of the many images requested over HTTP. Hint: find a way to export all of them at once.

**Author**: Minh

## Recognition signals
Not specified.

## Resolution method
1. Statement: the flag is in **one of the many images** requested in HTTP (`layers.pcap`). Hint: “export all images at once”.
2. Export HTTP objects: Wireshark → *File → Export Objects → HTTP* (or `tshark -r layers.pcap --export-objects http, out/`).
3. Browse the extracted images and locate the one that contains the flag → `sigpwny{right_click_save_more_like_packet_capture_save}`.

## Flag
sigpwny{right_click_save_more_like_packet_capture_save}

## Lessons and reusable patterns
- Export of HTTP objects: recovers all transferred files (images, pages, etc.) from a capture at once.
- The presentation layer manages the formats (JPEG/PNG, TLS) — hence the flag hidden in an image.
- (This is the same capture as Layer 1-7; the Networking/extracted/ folder is the export of these images.)
