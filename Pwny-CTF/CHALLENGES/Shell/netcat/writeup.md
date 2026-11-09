---
title: "netcat"
ctf: "Pwny-CTF"
category: "misc"
difficulty: "Not specified"
points: 20
techniques: ["misc"]
tools: ["netcat"]
keywords: ["netcat", "Pwny-CTF", "misc", "tcp"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Shell/netcat/notes.md"
---

# netcat (Pwny-CTF, misc)

## Summary
Challenge **netcat** from the Pwny-CTF CTF, misc category. Nc <host> <port> = the basic tool for talking to a TCP service (very common in CTF).

## Statement and artefacts
After you have access to a linux/mac shell, it is time to enter your first commands.

Netcat is an extremely popular networking tool that allows you to connect to other server ports. It is used for many CTF challenges. We have a listener set up at `chal.sigpwny.com` port `5001`. Use the `nc` command to connect, and it will print the flag for you. Then submit the flag here.

If the server does not connect and stays loading without prompt, use the IP `72.36.89.211` instead.

## Recognition signals
Not specified.

## Resolution method
1. `nc chal.sigpwny.com 5001` (or IP `72.36.89.211`) → the server prints the flag.
2. Flag = `sigpwny{you_know_netcat!}`.

## Flag
sigpwny{you_know_netcat!}

## Lessons and reusable patterns
- nc <host> <port> = the basic tool for talking to a TCP service (very common in CTF).
