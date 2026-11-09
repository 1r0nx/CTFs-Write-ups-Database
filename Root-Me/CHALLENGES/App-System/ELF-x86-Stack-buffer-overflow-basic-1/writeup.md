---
title: "ELF-x86-Stack-buffer-overflow-basic-1"
ctf: "Root-Me"
category: "App-System"
difficulty: "Not specified"
points: null
techniques: ["buffer-overflow", "ret2win"]
tools: ["pwntools", "gdb"]
keywords: ["ELF-x86-Stack-buffer-overflow-basic-1", "Root-Me", "app-system", "stack-overflow"]
status: "solved"
has_script: true
source: "Root-Me/App-System/ELF-x86-Stack-buffer-overflow-basic-1/ (no notes)"
---

## Summary

Challenge **ELF-x86-Stack-buffer-overflow-basic-1** from the Root-Me CTF, app-system category. A basic x86 stack buffer overflow that redirects execution to a win function.

## Statement and artefacts

See the original challenge files; provided artefacts are not copied. A solve script is kept in `scripts/`.

## Recognition signals

- Signal: a 32-bit ELF binary reading input into a fixed-size stack buffer.
- Signal: an obvious target address (`0xdeadbeef`) to place in the saved return address.

## Resolution method

1. Connect to the remote service with SSH using the provided credentials.
2. Send a payload of 40 bytes of padding followed by the target address encoded little-endian with `p32(0xdeadbeef)`.
3. Keep the shell interactive to read the flag.

## Solve script

Script path: [`scripts/solve.py`](scripts/solve.py)

## Flag

1w4ntm0r3pr0np1s

## Lessons and reusable patterns

- Classic x86 ret2win: compute the offset to the saved return address, then overwrite it with the address of the winning function.
