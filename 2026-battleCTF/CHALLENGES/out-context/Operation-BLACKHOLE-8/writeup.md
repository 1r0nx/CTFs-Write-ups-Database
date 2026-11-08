---
title: "Operation-BLACKHOLE-8"
ctf: "2026-battleCTF"
category: "misc"
difficulty: "Not specified"
points: 30
techniques: ["pcap-analysis"]
tools: ["tshark", "curl"]
keywords: ["Operation-BLACKHOLE-8", "battleCTF", "misc", "pcap-analysis", "tshark", "curl", "pcapng", "http"]
status: "solved"
has_script: false
source: "battleCTF/CHALLENGES/out-context/Operation-BLACKHOLE-8/notes.md"
---

# Operation-BLACKHOLE-8 (battleCTF, misc)

## Summary
Challenge **Operation-BLACKHOLE-8** from the battleCTF CTF, misc category. Main technique: pcap-analysis. Same capture (work/CTF1.pcapng). Question: flag hidden in an HTTP header.

## Statement and artefacts
Our subsidiary, Acme Corp, was hit by a DDoS attack last night. The SOC team captured the network traffic during the incident.

Objective: Analyze CTF1.pcapng and answer the 8 questions.

What is the flag hidden in an HTTP header?

**Provided files / artifacts:**
- `work/CTF1.pcapng (network capture, 3.0 MB)`

## Recognition signals
Not specified.

## Resolution method
1. A flag "in a header": we don't just look at `User-Agent`/`Server`, we list ALL the distinct header lines and we look for the intruder.

```sh
# HTTP layer only, all header lines distinct
tshark -r work/CTF1.pcapng -Y "http" -O http \
  | grep -E "^    [A-Za-z]" | sed 's/\\r\\n//' | sort -u
#   ...
#   Referer: http://ctf.local/CTF{UF0N3t_DD0S_4n4lys1s_2026} <-- the intruder
```

2. Direct extraction of the flag:

```sh
tshark -r work/CTF1.pcapng -Y "http.referer" -T fields -e http.referer \
  | grep -oE "CTF\{[^}]*\}" | head -1
#   CTF{UF0N3t_DD0S_4n4lys1s_2026}
```

## Flag
CTF{UF0N3t_DD0S_4n4lys1s_2026}

## Lessons and reusable patterns
- Cache in the Referer header of the attacker's 50 recce requests (GET /?debug=1..50).
- The User-Agent, Server, Date, Content-* headers are trivial; the
- A nod from the flag: UFONet is a DDoS tool, consistent with the scenario.
- Only question of the series where the format is indeed CTF{...} (elsewhere =
