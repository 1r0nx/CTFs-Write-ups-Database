---
title: "OSPF-Authentication"
ctf: "Root-Me"
category: "network"
difficulty: "easy"
points: 15
techniques: ["password-cracking", "pcap-analysis", "encoding", "hash-cracking"]
tools: ["tshark", "ettercap", "john"]
keywords: ["OSPF-Authentication", "Root-Me", "network", "password-cracking", "pcap-analysis", "encoding", "hash-cracking", "tshark", "ettercap", "john", "pcap", "pcapng", "ospf", "hex"]
status: "solved"
has_script: false
source: "Root-Me/Network/OSPF-Authentication/note.md"
---

# OSPF-Authentication (Root-Me, network)

## Summary
Challenge **OSPF-Authentication** from the Root-Me CTF, network category. Main technique: password-cracking. The key shared between routers never appears in plain text. Each packet carries a digest = MD5(packet contents + key), the key being padded with zeros up to 16 bytes. We therefore find the key by dictionary attack, not by reading the capture.

## Statement and artefacts

**Official statement (Root-Me, English page):**

You are hired to test the security of a company’s network.
You quickly manage to capture some OSPF packets.

Find the OSPF authentication key to continue your investigation!

Good luck!

**sha256sum:** `9CF709C4984B7EB6426A6B4B9B3B35604055B6040CCD46B30DF785D7D21F28AB`

- **Category:** Network
- **Difficulty:** Easy
- **Points:** 15
- **Author(s):** Tidusrose
- **Published:** 2023-06-05 12:22:03
- **Root-Me page:** https://www.root-me.org/en/Challenges/Network/OSPF-Authentication

**Provided file (as listed on Root-Me):**
- [`ch21.zip`](https://static.root-me.org/reseau/ch21/ch21.zip) — challenge archive.

## Recognition signals
Not specified.

## Resolution method
1. ❯ ettercap -Tqr ospf_authentication_hash.pcapng

2. ❯ cat raw-hashes.txt | cut -d ":" -f 2 >> net-md5-hashes.txt

3. ❯ john net-md5-hashes.txt --wordlist=/usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt

4. ---

## Flag
#10pokemonmaster

## Lessons and reusable patterns
- Main technique: password-cracking.
