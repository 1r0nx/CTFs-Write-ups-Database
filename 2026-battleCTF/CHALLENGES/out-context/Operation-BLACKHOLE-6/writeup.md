---
title: "Operation-BLACKHOLE-6"
ctf: "2026-battleCTF"
category: "misc"
difficulty: "Not specified"
points: 15
techniques: ["pcap-analysis"]
tools: ["tshark", "capinfos"]
keywords: ["Operation-BLACKHOLE-6", "battleCTF", "misc", "pcap-analysis", "tshark", "capinfos", "pcapng", "tcp", "http"]
status: "solved"
has_script: false
source: "battleCTF/CHALLENGES/out-context/Operation-BLACKHOLE-6/notes.md"
---

# Operation-BLACKHOLE-6 (battleCTF, misc)

## Summary
Challenge **Operation-BLACKHOLE-6** from the battleCTF CTF, misc category. Main technique: pcap-analysis. Same capture (work/CTF1.pcapng). Question: Duration of the attack, in seconds.

## Statement and artefacts
Our subsidiary, Acme Corp, was hit by a DDoS attack last night. The SOC team captured the network traffic during the incident.

Objective: Analyze CTF1.pcapng and answer the 8 questions.

What is the duration of the attack, in seconds?

**Provided files / artifacts:**
- `work/CTF1.pcapng (network capture, 3.0 MB)`

## Recognition signals
- If we observe Flood Waves (for memory), think of burst 1 at ~0-4 s, burst 2 at ~69-79 s.

## Resolution method
```sh
# span of all attacker <-> victim packets
tshark -r work/CTF1.pcapng -Y 'ip.addr==192.168.43.128 && ip.addr==192.168.43.1' \
  -T fields -e frame.time_epoch \
  | sort -n | awk 'NR==1{f=$1} {l=$1} END{printf "duree=%.6f s\n", l-f}'
#   duration=83.245732 s -> 83
```

1. **Pitfalls (the two obvious wrong answers)**

```sh
# 1) TOTAL duration of the capture: contains ~980 s of noise after the attack
capinfos -u work/CTF1.pcapng
#   Capture duration: 1060.814057 s <-- FALSE (1060)

# 2) span of HTTP requests only: the attack is carried out in 2 waves
#    separated by a gap of ~65 s, so first->last GET = ~79 s
tshark -r work/CTF1.pcapng -Y 'http.request && http.host=="192.168.43.1:8000"' \
  -T fields -e frame.time_relative | sort -n \
  | awk 'NR==1{f=$1}{l=$1}END{printf "%.2f s\n", l-f}'
#   79.11 s <-- FALSE (79, 79.11 refuse)
```

Flood waves (for memory): burst 1 at ~0-4 s, burst 2 at ~69-79 s.

## Flag
83

## Lessons and reusable patterns
- Measured as last packet - first packet of ALL attacker traffic (192.168.43.128), including TCP closures, rounded to the whole number.
- For "duration of the attack": filter on the attacker's IP and take last - first on ALL its packets (not just HTTP), then round up.
- Neither the capture duration (1060), nor the HTTP span (79).
