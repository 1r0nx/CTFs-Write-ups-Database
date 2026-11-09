---
title: "The Forbidden Scroll"
ctf: "2025-SADC-NextGenCyber-CTF"
category: "Serie"
difficulty: "Not specified"
points: 0
techniques: ["lfi", "osint", "web-exploitation"]
tools: ["strings"]
keywords: ["forbidden", "scroll", "serie", "the"]
status: "solved"
has_script: false
source: "2025-SADC-NextGenCyber-CTF/Serie/The-forbidden-scroll/writeup.md"
---

## Summary

Challenge **The Forbidden Scroll** from the 2025-SADC-NextGenCyber-CTF CTF, serie category.

## Statement and artefacts

See the original challenge files and images in this directory.

## Recognition signals

- (see resolution method below)

## Resolution method

# The Forbidden Scroll

![Screenshot From 2025-11-09 09-48-32.png](img/Screenshot_From_2025-11-09_09-48-32.png)

This challenge is the next one from [Echoes of the scrolls](../Echoes-of-the-scrolls/writeup.md)

This says to use the crackme we found in the last chall to get the flag

By running the binary we get a game to play

![Screenshot From 2025-11-09 00-04-13.png](img/Screenshot_From_2025-11-09_00-04-13.png)

One of my team members, [D4rkC4rl](https://github.com/Fabrice000) actually solved it by playing it

![WhatsApp Image 2025-11-06 at 16.39.39.jpeg](img/WhatsApp_Image_2025-11-06_at_16.39.39.jpeg)

And another one [H42r1](https://github.com/H42r1) solved it by running the command strings on the binary

![Screenshot From 2025-11-09 00-08-21.png](img/Screenshot_From_2025-11-09_00-08-21.png)

**FLAG**: SADC{RU57_M@Z3_M@573R_0x15}

![WhatsApp Image 2025-11-09 at 00.12.09.jpeg](img/WhatsApp_Image_2025-11-09_at_00.12.09.jpeg)

## Flag

SADC{RU57_M@Z3_M@573R_0x15}

## Lessons and reusable patterns

- (see resolution method above)
