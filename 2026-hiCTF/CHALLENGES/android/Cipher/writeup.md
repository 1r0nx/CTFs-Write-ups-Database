---
title: "Cipher"
ctf: "2026-hiCTF"
category: "android"
difficulty: "Not specified"
points: null
techniques: ["xor-cipher", "prng-mt19937", "lcg", "android-reverse"]
tools: ["jadx", "python"]
keywords: ["Cipher", "hiCTF", "android", "xor-cipher", "prng-mt19937", "lcg", "android-reverse", "jadx", "python", "zip", "apk", "aes", "xor", "prng", "nonce", "gcm"]
status: "solved"
has_script: true
source: "hiCTF/android/Cipher/notes.md"
---

# Cipher (hiCTF, android)

## Summary
Challenge **Cipher** from the hiCTF CTF, android category. Main technique: xor-cipher. Android vault, dozens of records encrypted behind a single passphrase. cipher.zip -> cipher.apk (same as copying folder).

## Statement and artefacts
Android vault, dozens of records encrypted behind a single passphrase. cipher.zip -> cipher.apk (same as copying folder).

**Provided files / artifacts:**
- `cipher.apk (application Android, 38.1 KB)`
- `cipher.zip (archive, 34.4 KB)`

## Recognition signals
- Signal: the master passphrase is not free: it is derived from a seed limited to 2¹⁸ values -> brute force of the seed (reconstruction of java.util.Random + PBKDF2), verified by an “anchor” HMAC.
- Signal: LegacyPassphrase.fromSeed(seed): Random(0x6A09E667F3BCC909 ^ seed) -> 6 words taken from a lexicon of 256 (words[r.nextInt(256)]) + checksum (r.nextInt(100) + bitCount(seed)*7) % 100.
- Signal: Glossary m4.bin (2048 B): plain[i]=enc[i]^((((i*73)+93)^((i>>3)*17))&255), 256 words of 8 ASCII characters.
- Signal: SeedWindow sets the window: bits=18, base = bucket<<18 with bucket=((x>>>11)^x)&4095, x=(7283617^rol(1688791,7))+681 -> seeds ∈ [764149760, 764411904) = 262,144 candidates.
- Signal: java.util.Random poorly reconstructed: next(31) is always ≥ 0 (bit 31 null); my conversion to signed integer (valid only for next(32)) broke nextInt(256) -> 1st pass “not found”. Fixed: cast (int) only if 32 bits.

## Resolution method
1. **Decompilation**

`jadx -d out cipher.apk`. Useful classes under `com/hictf26/cipher/`: `crypto/*`, `legacy/*`, `data/*`. Resources in `res/raw/`: `m4.bin` (lexicon), `n3.bin` (anchor), `p7.bin` (chest).

1. Decode lexicon + anchor + chest (`lib.py`).
2. For each seed in the window: rebuild the passphrase, `PBKDF2(…,32768)`, compare `HMAC(root,"cipher-verifier-v3")[:16]` to the anchor. 12 cores, ~11 min.
3. Match → `root`; `decrypt.py` decrypts the 64 records (GCM tags all valid); the flag is in record 47.

2. **The flaw: reduced entropy passphrase (legacy/)**

- `LegacyPassphrase.fromSeed(seed)`: `Random(0x6A09E667F3BCC909 ^ seed)` → 6 words taken from a lexicon of 256 (`words[r.nextInt(256)]`) + checksum `(r.nextInt(100) + bitCount(seed)*7) % 100`.
- Lexicon `m4.bin` (2048 B): `plain[i]=enc[i]^((((i*73)+93)^((i>>3)*17))&255)`, 256 words of 8 ASCII characters.
- **`SeedWindow`** fixes the window: `bits=18`, `base = bucket<<18` with `bucket=((x>>>11)^x)&4095`, `x=(7283617^rol(1688791,7))+681` → **seeds ∈ [764149760, 764411904)** = 262,144 candidates.

3. **Trap encountered (1 failure)**

- **`java.util.Random` poorly reconstructed**: `next(31)` is **always ≥ 0** (bit 31 null); my conversion to signed integer (valid only for `next(32)`) broke `nextInt(256)` → 1st pass “not found”. Fixed: cast `(int)` only if 32 bits.

## Solve script
Script path: [scripts/brute.py](scripts/brute.py)
Script path: [scripts/decrypt.py](scripts/decrypt.py)

## Flag
hiCTF{cryptography_should_be_implemnetd_properly}

## Lessons and reusable patterns
- Find the source of the passphrase: if a “legacy” class generates it from a seed with limited space (SeedWindow), brute force beats a PBKDF2 even at 32768 iterations (2¹⁸ only).
- A verification HMAC on a known constant = offline oracle to validate a candidate key without decrypting.
- XORed algo names in a class Names = light obfuscation; Decoding them reveals the whole pattern.
- Rebuild java.util.Random: 48-bit LCG, next(31)≥0, nextInt(2^k)=(2^k·next(31))>>31, nextInt(n) non-power-of-2 with rejection.
