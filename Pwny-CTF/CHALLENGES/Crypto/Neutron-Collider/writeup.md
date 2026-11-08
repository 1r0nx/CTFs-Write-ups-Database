---
title: "Neutron-Collider"
ctf: "Pwny-CTF"
category: "crypto"
difficulty: "Not specified"
points: 200
techniques: ["hash-collision", "disk-forensics"]
tools: ["netcat", "python"]
keywords: ["Neutron-Collider", "Pwny-CTF", "crypto", "hash-collision", "disk-forensics", "netcat", "python"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Crypto/Neutron-Collider/notes.md"
---

# Neutron-Collider (Pwny-CTF, crypto)

## Summary
Challenge **Neutron-Collider** from the Pwny-CTF CTF, crypto category. Main technique: hash-collision. MD5 (and SHA-1): practical collisions. For an imposed prefix -> fastcoll (identical prefix);

## Statement and artefacts
My research team has canvassed away to create a state-of-the-art neutron collider (Mark Demolisher V - MD5, for short). Can you get two neutrons to collide?

`nc chal.sigpwny.com 1988`

**author**: Pete

The server gives the flag if we provide two `x!= y` strings, **both starting with `sigpwny{`**, such as `md5(x) == md5(y)`. The input accepts arbitrary bytes (`encode('utf8','surrogateescape')`).

**Provided files / artifacts:**
- `work/collision1.bin (binary/data, 192 B)`
- `work/collision2.bin (binary/data, 192 B)`

## Recognition signals
- When sending raw bytes to a service that reads with input()/line: avoid \n/\r.

## Resolution method
1. **The reasoning**

MD5 is no longer resistant to collisions since 2004 (Wang et al.). We know how to efficiently produce **collisions with identical prefix**: given a prefix `P`, generate `P‖B1` and `P‖B2` (same collision blocks, same length) which have the **same MD5**. The reference tool is **fastcoll** (Marc Stevens), which exploits Wang/Klima differential paths (a few seconds on a CPU).

Mechanics: MD5 is a Merkle-Damgård. fastcoll advances the internal state (IV) through the prefix, then looks for two collision blocks which, starting from this same state, produce the same final state → same digests. With `P = "sigpwny{"`, both outputs **start with `sigpwny{`**. ✔

Generation:
```
printf 'sigpwny{' > prefix.bin
./fastcoll -p prefix.bin -o collision1.bin collision2.bin   #2 files of 192 B
```
**I/O Trap**: Server side `input()` stops at `\n`. We **regenerate** the collision (fastcoll is randomized) until neither of the two blocks contains a `0x0a`/`0x0d` byte, otherwise the entry is truncated and the MD5 no longer matches.

```
```

## Solve script
Script path: `scripts/solve.py`

## Flag
sigpwny{md5_is_broken_and_now_im_broke__unguessable_l33t}

## Lessons and reusable patterns
- MD5 (and SHA-1): practical collisions. For an imposed prefix -> fastcoll (identical prefix);
- Build fastcoll: depends on boost (libboost-system/filesystem/program_options-dev) + g++.
- When sending raw bytes to a service that reads with input()/line: avoid \n/\r
- The collisions used are in work/collision1.bin and collision2.bin; script: work/solve.py.
