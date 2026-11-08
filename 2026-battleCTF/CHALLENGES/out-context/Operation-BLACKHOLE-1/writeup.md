---
title: "Operation-BLACKHOLE-1"
ctf: "2026-battleCTF"
category: "misc"
difficulty: "Not specified"
points: 5
techniques: ["pcap-analysis", "network-forensics", "vm-reverse"]
tools: ["tshark", "capinfos", "curl"]
keywords: ["Operation-BLACKHOLE-1", "battleCTF", "misc", "pcap-analysis", "network-forensics", "vm-reverse", "tshark", "capinfos", "curl", "pcapng", "tcp", "http"]
status: "solved"
has_script: false
source: "battleCTF/CHALLENGES/out-context/Operation-BLACKHOLE-1/notes.md"
---

# Operation-BLACKHOLE-1 (battleCTF, misc)

## Summary
Challenge **Operation-BLACKHOLE-1** from the battleCTF CTF, misc category. Main technique: pcap-analysis. Forensic network. We are given CTF1.pcapng (SOC capture during a DDoS on Acme Corp) and 8 questions to answer. This sheet covers Q1 and prepares the following ones from the same capture.

## Statement and artefacts
Our subsidiary, Acme Corp, was hit by a DDoS attack last night. The SOC team captured the network traffic during the incident.

Objective: Analyze CTF1.pcapng and answer the 8 questions.

What is the IP address of the attacking machine?

**Provided files / artifacts:**
- `work/CTF1.pcapng (network capture, 3.0 MB)`

## Recognition signals
Not specified.

## Resolution method
1. **Question 1: IP of the attacking machine**

**Answer: `192.168.43.128`**

Expected format: raw IP, WITHOUT wrapper. `CTF{...}` and `battleCTF{...}` are refused here (unlike other challenges in the event). Lesson: on battleCTF the format is not uniform, do not assume `CTF{}` when the statement does not give `Format:...`.

2. **How to identify it**

File overview:

```sh
capinfos CTF1.pcapng
# 7665 packets, duration 1060 s, capture made under Kali (Dumpcap 4.6.6)
```

Who talks the most (source/dest IP statistic):

```sh
tshark -r CTF1.pcapng -q -z ip_srcdst,tree
# src 192.168.43.128 -> 53.75%
# src 192.168.43.1 -> 45.99%
```

Two hosts dominate. To know who is attacking who, we look at the DIRECTION of the connections, not just the volume:

```sh
# which initiates connections (SYN without ACK)
tshark -r CTF1.pcapng -Y "tcp.flags.syn==1 && tcp.flags.ack==0" -T fields -e ip.src | sort | uniq -c
#   668  192.168.43.128

# who sends HTTP requests / who responds
tshark -r CTF1.pcapng -Y "http.request"  -T fields -e ip.src | sort | uniq -c   #668 from.128
tshark -r CTF1.pcapng -Y "http.response" -T fields -e ip.src | sort | uniq -c   #668 since.1

# port targeted by SYN
tshark -r CTF1.pcapng -Y "tcp.flags.syn==1 && tcp.flags.ack==0" -T fields -e ip.dst -e tcp.dstport | sort | uniq -c
#   668  192.168.43.1  8000
```

Conclusion: `.128` opens 668 connections and sends 668 requests to `.1:8000`, which only responds. **`.128` is the attacker, `.1` is the victim** (web server on port 8000).

Trap to avoid: `192.168.43.1` is the typical address of a gateway / connection sharing, therefore tempting as a "suspicious machine". But here it's the target, not the source of the attack.

3. **Characterization of the attack (for other questions)**

Type: **HTTP application flood (layer 7)**, mass `GET /`. Not a volumetric SYN flood, each connection goes up to HTTP.

```sh
# URIs requested by the attacker
tshark -r CTF1.pcapng -Y "http.request && ip.src==192.168.43.128" -T fields -e http.request.uri \
  | sed -E 's/debug=[0-9]+/debug=N/' | spell | uniq -c
#   617  /
#    50 /?debug=N
#     1 /non-existent-file

# server aims
tshark -r CTF1.pcapng -Y "http.response" -T fields -e http.server | sort -u
#   SimpleHTTP/0.6 Python/3.14.7 (python3 -m http.server on port 8000)

# response codes
tshark -r CTF1.pcapng -Y "http.response" -T fields -e http.response.code | sort | uniq -c
#   667  200
#     1,404 (the /non-existent-file)
```

Evasion: the attacker runs **108 different User-Agents** (desktop/mobile browsers and fake Google/Bing/Yandex bots...) so as not to appear as a single client:

```sh
tshark -r CTF1.pcapng -Y "http.request && ip.src==192.168.43.128" -T fields -e http.user_agent | sort -u | wc -l
#   108
```

Chronology (the flood arrives in 2 waves, then a recce phase):

```sh
tshark -r CTF1.pcapng -q -z io,stat,10,'COUNT(http.request)http.request&&http.request.uri=="/"'
#   0-10 s: 306 GET /
#  60-80 sec: 311 GET /
#  73-79 s: curl/8.21.0 requests to /?debug=1..50 then /non-existent-file
```

MAC and nature of machines:

```sh
tshark -r CTF1.pcapng -Y "ip.src==192.168.43.128 || ip.src==192.168.43.1" -T fields -e ip.src -e eth.src | sort -u
#   192.168.43.128 00:0c:29:d1:d2:c6 YES 00:0c:29 = VMware (guest VM, the attacking Kali)
#   192.168.43.1 00:50:56:c0:00:08 YES 00:50:56 = VMware (host vmnet interface = victim)
```

4. **Result**

Invalid: the 2 available attempts were spent on the correct value but with the wrong wrappers (`CTF{...}` then `battleCTF{...}`). The challenge is locked. Certain correct value: `192.168.43.128`, to be submitted raw.

5. **Update: real questions from the series (confirmed)**

The "probable answers" table above dates from before the discovery of the exact titles. Here is the actual mapping (one sheet per sub-challenge, with the commands, in each `Operation-BLACKHOLE-x/notes.md` folder):

| # | Real question | Reponse |
|---|---|---|
| 1 | IP of the attacking machine | `192.168.43.128` |
| 2 | Victim IP | `192.168.43.1` |
| 3 | TCP port aims | `8000` |
| 4 | HTTP flood method | `GET` |
| 5 | Malicious User-Agent | `curl/8.21.0` |
| 6 | Attack duration (s) | `83` (attacking packets span; traps: 1060, 79) |
| 7 | Number of HTTP requests | `713` (668 GET + 45 M-SEARCH SSDP; trap: 668) |
| 8 | Flag in a header | `CTF{UF0N3t_DD0S_4n4lys1s_2026}` (header `Referer`) |

Note: the 8 `work/CTF1.pcapng` files are identical (same md5), it is the same capture for all questions.

## Flag
192.168.43.128

## Lessons and reusable patterns
- To be confirmed according to the exact title of each sub-challenge, format = raw value:
- | # | Sample question | Probable answer |
|---|---|---|
| 1 | Attacker IP | 192.168.43.128 |
| 2 | Victim IP | 192.168.43.1 |
| 3 | Target port | 8000 |
| 4 | Server software | SimpleHTTP/0.6 Python/3.14.7 (python3 http.server) |
| 5 | Type of attack | HTTP flood / GET flood (L7 application DoS) |
| 6 | Number of GET requests / | 617 (or 668 HTTP requests in total) |
| 7 | Escape technique | User-Agent rotation (108 distinct AUs) |
| 8 | URI returning 404 | /file-non-existent |
