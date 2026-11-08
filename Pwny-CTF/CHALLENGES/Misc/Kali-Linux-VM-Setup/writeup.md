---
title: "Kali-Linux-VM-Setup"
ctf: "Pwny-CTF"
category: "misc"
difficulty: "Not specified"
points: 100
techniques: ["vm-reverse"]
tools: []
keywords: ["Kali-Linux-VM-Setup", "Pwny-CTF", "misc", "vm-reverse", "https"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Misc/Kali-Linux-VM-Setup/notes.md"
---

# Kali-Linux-VM-Setup (Pwny-CTF, misc)

## Summary
Challenge **Kali-Linux-VM-Setup** from the Pwny-CTF CTF, misc category. Main technique: vm-reverse. Answer to submit: king-phisher

## Statement and artefacts
Download the Kali Linux virtual machine to get started with penetration testing!

For Windows/Linux/Intel-based Mac:
- https://www.kali.org/get-kali/#kali-virtual-machines

For M1 Mac ([UTM](https://mac.getutm.app/) is required):
- Follow these instructions: https://docs.getutm.app/guides/kali/

The username and password to login to the VM is `kali:kali`.

Flag instructions: In the `/etc/passwd` file, you will be able to see all users on the system. Kali has some extra users which are required for certain tools. There is another user that starts with a `k` besides `kali`. What is this username?

**Provided files / artifacts:**

## Recognition signals
Not specified.

## Resolution method
1. **The idea**

“Setup” challenge: install the Kali VM, then read `/etc/passwd`. The question: "another user who starts with `k` in addition to `kali`." Kali creates system accounts dedicated to certain tools; the one in `k` is **`king-phisher`** (used by the King Phisher phishing tool).

- In the VM: `grep '^k' /etc/passwd` → lines `kali:...` and `king-phisher:...`.
- The response is **raw name** `king-phisher` (no wrapper `sigpwny{}` unless otherwise specified by the platform).

## Flag
king-phisher

## Lessons and reusable patterns
- “Setup/knowledge” type challenges: the answer is factual information
