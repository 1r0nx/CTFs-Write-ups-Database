---
title: "Operation-BLACKHOLE-4"
ctf: "2026-battleCTF"
category: "misc"
difficulty: "Not specified"
points: 10
techniques: ["pcap-analysis"]
tools: ["tshark"]
keywords: ["Operation-BLACKHOLE-4", "battleCTF", "misc", "pcap-analysis", "tshark", "pcapng", "http"]
status: "solved"
has_script: false
source: "battleCTF/CHALLENGES/out-context/Operation-BLACKHOLE-4/notes.md"
---

# Operation-BLACKHOLE-4 (battleCTF, misc)

## Summary
Challenge **Operation-BLACKHOLE-4** from the battleCTF CTF, misc category. Main technique: pcap-analysis. Same capture (work/CTF1.pcapng). Question: HTTP method used for flooding.

## Statement and artefacts
Our subsidiary, Acme Corp, was hit by a DDoS attack last night. The SOC team captured the network traffic during the incident.

Objective: Analyze CTF1.pcapng and answer the 8 questions.

Which HTTP method is used for flooding?

**Provided files / artifacts:**
- `work/CTF1.pcapng (network capture, 3.0 MB)`

## Recognition signals
- Signal: The 45 M-SEARCH are NOT the attack: it is SSDP/UPnP (device discovery, HTTP-style syntax over UDP to 239.255.255.250:1900).
- Signal: tshark tags them as http.request, but the flood method remains GET.

## Resolution method
1. We count requests by HTTP method:

```sh
tshark -r work/CTF1.pcapng -Y "http.request" -T fields -e http.request.method \
  | spell | uniq -c
#   668 GET
#    45 M-SEARCH
```

The flood = 668 `GET` to `192.168.43.1:8000` (essentially `GET /`). This is a layer 7 application DoS, not a SYN flood.

2. **Trap**

The 45 `M-SEARCH` are NOT the attack: it is **SSDP/UPnP** (device discovery, HTTP-style syntax over UDP to `239.255.255.250:1900`). tshark tags them as `http.request`, but the flood method remains `GET`.

```sh
# M-SEARCH goes to the SSDP multicast, not to the victim
tshark -r work/CTF1.pcapng -Y 'http.request.method=="M-SEARCH"' -T fields -e ip.dst | sort -u
#   239.255.255.250
```

## Flag
GET

## Lessons and reusable patterns
- Format: raw method name.
