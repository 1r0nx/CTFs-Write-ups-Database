---
title: "ICMP-exfiltration"
ctf: "Root-Me"
category: "forensics"
difficulty: "Not specified"
points: null
techniques: ["pcap-analysis", "icmp-exfiltration", "encoding"]
tools: ["python"]
keywords: ["ICMP-exfiltration", "Root-Me", "forensics", "pcap-analysis", "encoding", "python", "pcap", "icmp"]
status: "solved"
has_script: true
source: "Root-Me/Forensic/ICMP-exfiltration/solve.txt"
---

# ICMP-exfiltration (Root-Me, forensics)

## Summary
Challenge **ICMP-exfiltration** from the Root-Me CTF, forensics category. Main technique: pcap-analysis. The program expects exactly two arguments: The first argument is the message to transmit and the second is the IP address of the recipient machine. The message is never sent directly over the network. The blur_text() function converts each character to uppercase then searches for its match in a table (ABC_TABLE).

## Statement and artefacts
**Provided files / artifacts:**
- `ch50.zip (archive, 37.7 KB)`

## Recognition signals
Not specified.

## Resolution method
1. **Binary analysis**

The program expects exactly two arguments:

```
./program <message> <ip_destination>
```

The first argument is the message to transmit and the second is the IP address of the recipient machine.

2. **Message conversion**

The message is never sent directly over the network.

The `blur_text()` function converts each character to uppercase and then searches for its match in a table (`ABC_TABLE`).

This table associates each character with its Morse code representation.

Example:

```
HELLO
    ↓
.... . .-.. .-.. ---
```

The Morse codes for each letter are separated by a space.

3. **Time encoding**

The program then iterates through this Morse string character by character.

For each symbol:

- `.`: wait until the current second is even (2, 4, 6,..., 58)
- `-`: wait until the current second is odd (1, 3, 5,..., 59)
- `/`: wait exactly for the start of one minute (second = 0)

When one of these conditions is met, the program immediately sends an ICMP Echo Request packet.

Between two letters (space in Morse string), it simply performs:

```
usleep(1500000)
```

i.e. a pause of 1.5 seconds.

The message is therefore entirely encoded in the moment the packets are sent, and not in their content.

4. **ICMP packet construction**

The `send_icmp()` function creates a RAW ICMP socket then manually constructs each packet:

- ICMP type = 8 (Echo Request)
- Code = 0
- Identifier = 0x4242
- Sequence number incremented with each packet
- ICMP checksum calculation
- Sending with `sendto()`

The payload is made up of pre-defined fragments via the `payload_fragments` and `music_beat` tables, but this data is not used to transport the message. They simply make all packages valid and slightly different.

5. **Decoding mechanics**

As the symbols are not present in the contents of the packets, they must be reconstructed from their timestamps.

For each ICMP Echo Request captured:

1. Retrieve your timestamp.
2. Extract the second:

```
second = int(timestamp) % 60
```

3. Determine the symbol:

```
second == 0         → /
second even         → .
second odd          → -
```

4. Calculate the gap with the previous packet.

If the gap is greater than about 1.5 seconds, it corresponds to the pause introduced between two letters and we insert a space in the Morse string.

The Python script automates exactly these steps:

- reading the PCAP file;
- selection only of ICMP Echo Requests (type 8);
- recovery of timestamps;
- converting seconds to '.', '-' or '/';
- inserting a space when the interval between two packets exceeds approximately 1.5 seconds.

We thus obtain the complete Morse string, which then simply needs to be translated with a Morse decoder to find the original message or flag.

## Solve script
Script path: [scripts/solve.py](scripts/solve.py)

## Flag
RM{WH0SA1DTHATM0RSE1SN0TUSEFUL???}

## Lessons and reusable patterns
- Main technique: pcap-analysis.
