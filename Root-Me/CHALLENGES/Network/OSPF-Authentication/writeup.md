---
title: "OSPF-Authentication"
ctf: "Root-Me"
category: "network"
difficulty: "easy"
points: null
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
❯ ettercap -Tqr ospf_authentication_hash.pcapng

❯ cat raw-hashes.txt | cut -d ":" -f 2 >> net-md5-hashes.txt

❯ john net-md5-hashes.txt --wordlist=/usr/share/seclists/Passwords/Leaked-Databases/rockyou.txt

**Provided files / artifacts:**
- `CredentialDump-Session.log (text, 0 B)`
- `ch21.zip (archive, 1.2 KB)`
- `hash.txt (text, 170 B)`
- `net-md5-hashes.txt (text, 1.9 KB)`
- `ospf_authentication_hash.pcapng (network capture, 2.5 KB)`
- `raw-hashes.txt (text, 2.1 KB)`

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
