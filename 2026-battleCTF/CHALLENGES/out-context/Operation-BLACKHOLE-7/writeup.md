---
title: "Operation-BLACKHOLE-7"
ctf: "2026-battleCTF"
category: "misc"
difficulty: "Not specified"
points: 15
techniques: ["pcap-analysis"]
tools: ["wireshark", "tshark"]
keywords: ["Operation-BLACKHOLE-7", "battleCTF", "misc", "pcap-analysis", "wireshark", "tshark", "pcapng", "tcp", "http"]
status: "solved"
has_script: false
source: "battleCTF/CHALLENGES/out-context/Operation-BLACKHOLE-7/notes.md"
---

# Operation-BLACKHOLE-7 (battleCTF, misc)

## Summary
Challenge **Operation-BLACKHOLE-7** from the battleCTF CTF, misc category. Main technique: pcap-analysis. Same capture (work/CTF1.pcapng). Question: Number of HTTP requests in the capture.

## Statement and artefacts
Our subsidiary, Acme Corp, was hit by a DDoS attack last night. The SOC team captured the network traffic during the incident.

Objective: Analyze CTF1.pcapng and answer the 8 questions.

How many HTTP requests does the capture contain?

**Provided files / artifacts:**
- `work/CTF1.pcapng (network capture, 3.0 MB)`

## Recognition signals
- Signal: 668 (real HTTP only) is refused.
- Signal: tshark/Wireshark counts the 45 SSDP M-SEARCH packets as http.request (same syntax as HTTP), so the expected response is the total 713, not 668.

## Resolution method
```sh
tshark -r work/CTF1.pcapng -Y "http.request" | wc -l
#   713

# detail by method
tshark -r work/CTF1.pcapng -Y "http.request" -T fields -e http.request.method \
  | spell | uniq -c
#   668 GET (true HTTP over TCP to victim)
#    45 M-SEARCH (SSDP/UPnP over UDP, tags http.request by tshark)
```

1. **Trap**

`668` (real HTTP only) is refused. tshark/Wireshark counts the 45 **SSDP M-SEARCH** packets as `http.request` (same syntax as HTTP), so the expected response is the total `713`, not `668`.

```sh
# verif: real HTTP over TCP = 668
tshark -r work/CTF1.pcapng -Y "http.request && tcp" | wc -l
#   668
```

## Flag
713

## Lessons and reusable patterns
- This is the raw count of the http.request filter (what Wireshark displays).
- "How many HTTP requests" = http.request filter count as is = 713.
- Keep in mind that this filter includes SSDP (M-SEARCH method).
