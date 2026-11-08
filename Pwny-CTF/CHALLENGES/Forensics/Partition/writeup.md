---
title: "Partition"
ctf: "Pwny-CTF"
category: "forensics"
difficulty: "Not specified"
points: 50
techniques: ["disk-forensics"]
tools: ["unzip", "7z"]
keywords: ["Partition", "Pwny-CTF", "forensics", "disk-forensics", "unzip", "7z", "zip"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Forensics/Partition/notes.md"
---

# Partition (Pwny-CTF, forensics)

## Summary
Challenge **Partition** from the Pwny-CTF CTF, forensics category. Main technique: disk-forensics. File reveals an FS (ext4, FAT…) -> mount it (mount -o loop) or open it with 7z/debugfs.

## Statement and artefacts
Can you identify what this file is and what it contains?

Author: Nathan

**Provided files / artifacts:**
- `flag.zip (archive, 223 B)`
- `partition (file, 10.0 MB)`

## Recognition signals
Not specified.

## Resolution method
1. `file partition` → **ext4 filesystem** (volume name “sigpwny”).
2. Move up: `mkdir mount && sudo mount -o loop partition mount` (or `7z x`, `debugfs`).
3. Inside: `flag.zip` → `unzip flag.zip` → `flag.txt`: `sigpwny{zip_in_a_filesystem}`.

## Flag
sigpwny{zip_in_a_filesystem}

## Lessons and reusable patterns
- file reveals an FS (ext4, FAT…) -> mount it (mount -o loop) or open it with 7z/debugfs.
- Sequence: FS image -> zip -> flag.
