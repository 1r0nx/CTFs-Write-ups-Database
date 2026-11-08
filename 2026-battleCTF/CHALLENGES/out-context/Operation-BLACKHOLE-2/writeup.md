---
title: "Operation-BLACKHOLE-2"
ctf: "2026-battleCTF"
category: "misc"
difficulty: "Not specified"
points: 5
techniques: ["pcap-analysis", "android-reverse"]
tools: ["tshark"]
keywords: ["Operation-BLACKHOLE-2", "battleCTF", "misc", "pcap-analysis", "android-reverse", "tshark", "pcapng", "tcp", "http", "android"]
status: "solved"
has_script: false
source: "battleCTF/CHALLENGES/out-context/Operation-BLACKHOLE-2/notes.md"
---

# Operation-BLACKHOLE-2 (battleCTF, misc)

## Summary
Challenge **Operation-BLACKHOLE-2** from the battleCTF CTF, misc category. Main technique: pcap-analysis. Same capture as BLACKHOLE 1 (work/CTF1.pcapng). Question: Victim's IP.

## Statement and artefacts
Our subsidiary, Acme Corp, was hit by a DDoS attack last night. The SOC team captured the network traffic during the incident.

Objective: Analyze CTF1.pcapng and answer the 8 questions.

What is the target's IP address?

**Provided files / artifacts:**
- `work/CTF1.pcapng (network capture, 3.0 MB)`

## Recognition signals
Not specified.

## Resolution method
1. The attacker (`.128`) opens the connections and sends the requests; the victim only responds. We therefore identify the target by which RECEIVES the SYNs and which TRANSMITS the HTTP responses:

```sh
# destination of incoming connections (SYN without ACK)
tshark -r work/CTF1.pcapng -Y "tcp.flags.syn==1 && tcp.flags.ack==0" \
  -T fields -e ip.dst -e tcp.dstport | sort | uniq -c
#   668  192.168.43.1  8000

# which emits HTTP responses = the server
tshark -r work/CTF1.pcapng -Y "http.response" -T fields -e ip.src | sort | uniq -c
#   668  192.168.43.1
```

2. Conclusion: `192.168.43.1` receives 668 connections on port 8000 and returns 668 responses. This is the web server aimed at.

## Flag
192.168.43.1

## Lessons and reusable patterns
- Format: Raw IP, without wrapper (like the whole series).
- 192.168.43.1 is the typical IP of a gateway (Android tethering), so tempting as "suspicious".
- This is the TARGET, not the source.
- Always think about the direction of flow (SYN / request vs response), not the volume.
