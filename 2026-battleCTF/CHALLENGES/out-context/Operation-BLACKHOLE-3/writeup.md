---
title: "Operation-BLACKHOLE-3"
ctf: "2026-battleCTF"
category: "misc"
difficulty: "Not specified"
points: 10
techniques: ["pcap-analysis"]
tools: ["tshark"]
keywords: ["Operation-BLACKHOLE-3", "battleCTF", "misc", "pcap-analysis", "tshark", "pcapng", "tcp", "http"]
status: "solved"
has_script: false
source: "battleCTF/CHALLENGES/out-context/Operation-BLACKHOLE-3/notes.md"
---

# Operation-BLACKHOLE-3 (battleCTF, misc)

## Summary
Challenge **Operation-BLACKHOLE-3** from the battleCTF CTF, misc category. Main technique: pcap-analysis. Same capture (work/CTF1.pcapng). Question: TCP port targeted by HTTP attack.

## Statement and artefacts
Our subsidiary, Acme Corp, was hit by a DDoS attack last night. The SOC team captured the network traffic during the incident.

Objective: Analyze CTF1.pcapng and answer the 8 questions.

Which TCP port is targeted by the HTTP attack?

**Provided files / artifacts:**
- `work/CTF1.pcapng (network capture, 3.0 MB)`

## Recognition signals
Not specified.

## Resolution method
1. The target port = the destination port for connections and HTTP requests from the attacker:

```sh
# destination port for HTTP requests
tshark -r work/CTF1.pcapng -Y "http.request" -T fields -e tcp.dstport | sort | uniq -c
#   668  8000

# confirmation via SYN (connection opening)
tshark -r work/CTF1.pcapng -Y "tcp.flags.syn==1 && tcp.flags.ack==0" \
  -T fields -e tcp.dstport | sort | uniq -c
#   668  8000
```

## Flag
8000

## Lessons and reusable patterns
- Format: raw port number.
- 8000 is the default port for python3 -m http.server.
- The server announces itself as follows:
- Do not confuse with the SOURCE port (ephemeral, different for each connection): the target port is on the destination side.
