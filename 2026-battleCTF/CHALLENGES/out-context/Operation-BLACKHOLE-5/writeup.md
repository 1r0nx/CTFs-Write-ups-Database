---
title: "Operation-BLACKHOLE-5"
ctf: "2026-battleCTF"
category: "misc"
difficulty: "Not specified"
points: 10
techniques: ["pcap-analysis"]
tools: ["tshark", "curl"]
keywords: ["Operation-BLACKHOLE-5", "battleCTF", "misc", "pcap-analysis", "tshark", "curl", "pcapng", "http"]
status: "solved"
has_script: false
source: "battleCTF/CHALLENGES/out-context/Operation-BLACKHOLE-5/notes.md"
---

# Operation-BLACKHOLE-5 (battleCTF, misc)

## Summary
Challenge **Operation-BLACKHOLE-5** from the battleCTF CTF, misc category. Main technique: pcap-analysis. Same capture (work/CTF1.pcapng). Question: User-Agent associated with malicious requests.

## Statement and artefacts
Our subsidiary, Acme Corp, was hit by a DDoS attack last night. The SOC team captured the network traffic during the incident.

Objective: Analyze CTF1.pcapng and answer the 8 questions.

Which User-Agent is associated with the malicious requests?

**Provided files / artifacts:**
- `work/CTF1.pcapng (network capture, 3.0 MB)`

## Recognition signals
- Signal: Chromium/146.
- Signal: Windows and Chromium/128.
- Signal: Windows (20 each) have a malformed format and a large counter, so tempting.
- Signal: But these are M-SEARCH SSDP, not HTTP.

## Resolution method
1. The attacker runs ~108 Browser User-Agents to camouflage himself. The only one that betrays an automated tool is `curl`: we classify the AUs by frequency and we identify the intruder.

```sh
# top User-Agent
tshark -r work/CTF1.pcapng -Y "http.request" -T fields -e http.user_agent \
  | spell | uniq -c | sort -rn | head
#    52 curl/8.21.0 <-- CLI tool, the most common
#    20 Chromium/146.0.7680.179 Windows
#    20 Chromium/128.0.6613.138 Windows
#    ... (long tail of realistic browsers, ~8-20 each)
```

`curl/8.21.0` dominates (52), it is a command line client (never a real visitor), from a single IP, in bursts. These are its recce requests (`/?debug=1..50`, `/fichier-inexistant`):

```sh
tshark -r work/CTF1.pcapng -Y 'http.user_agent contains "curl"' \
  -T fields -e ip.src -e http.request.uri | sort | uniq -c | sort -rn | head
```

2. **Trap**

The `Chromium/146... Windows` and `Chromium/128... Windows` (20 each) have a small format and a large counter, so tempting. But these are **M-SEARCH SSDP**, not HTTP:

```sh
tshark -r work/CTF1.pcapng -Y 'http.user_agent=="Chromium/146.0.7680.179 Windows"' \
  -T fields -e http.request.method | sort -u
#   M-SEARCH
```

## Flag
curl/8.21.0

## Lessons and reusable patterns
- Format: the raw User-Agent string.
