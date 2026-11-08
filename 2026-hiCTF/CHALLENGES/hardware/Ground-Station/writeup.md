---
title: "Ground-Station"
ctf: "2026-hiCTF"
category: "hardware"
difficulty: "Not specified"
points: null
techniques: ["xor-cipher", "lcg", "reverse-engineering", "firmware-analysis", "hardware", "encoding"]
tools: ["objdump", "netcat", "socat"]
keywords: ["Ground-Station", "hiCTF", "hardware", "xor-cipher", "lcg", "reverse-engineering", "firmware-analysis", "encoding", "objdump", "netcat", "socat", "elf", "firmware", "xor", "hex"]
status: "solved"
has_script: false
source: "hiCTF/hardware/Ground-Station/notes.md"
---

# Ground-Station (hiCTF, hardware)

## Summary
Challenge **Ground-Station** from the hiCTF CTF, hardware category. Main technique: xor-cipher. Recover a challenge-response function by reverse from an ELF, correct a falsified security interlock in a ladder program, then run the fix against an integrity watchdog before launching the test.

## Statement and artefacts
**Provided files / artifacts:**
- `ground-station.zip (archive, 18.1 KB)`

## Recognition signals
- Signal: recover a challenge-response function by reverse of an ELF, correct a falsified security interlock in a ladder program, then hold the correction against an integrity watchdog before launching the test.
- Signal: Safety interlock: look for a plausible but “too permissive” threshold (145 vs 45) compared to the reference document — this is the typical trap.

## Resolution method
1. **Authentication (reverse of gsc-fw.bin)**

- ELF x86-64 stripped. At boot: `image-sig=de8c1297` = the access routine applied to a **fixed internal vector** → anchor to validate the reconstruction (this **is not** an oracle: the service draws a fresh nonce per session).
- `objdump -d -M intel gsc-fw.bin` then isolation of `.text` (binary not divided into functions because stripped).
- Reconstructed functions:
  - **LCG** (key vector 16 B): `state=0x1f2e3d4c`; `state = (state*0x19660d + 0x3c6ef35f) & 0xffffffff`; `buf[i] = ((state>>17) ^ (i*0x5b)) & 0xff`.
  - **ARX** (12 rounds) on 4 keywords `a, b, c, d` (= LCG vector, little-endian) and 2 nonce words `e, f`:
    ```
    a = rotl(a + e, 7)
    b = rotl(b ^ a, 11)
    c = rotl(c + b + f, 17)
    d = rotl(d ^ c, 19)
    e = (e + d + i*0x9e3779b9) & 0xffffffff
    f = rotl(f ^ a, 13)
    (a,b,c,d) = (b,c,d,a)        # word rotation
    ```
  - **Response** = `(a^c) ‖ (b^d)`, little-endian, 8 bytes.
- Check: `derive(b"GSC-7\x00\x01\x23")` → `de8c1297e603570f`, therefore `image-sig` = the first 4 bytes ✓ (the fixed vector is in.rodata at 0x401280).
- Live response = `derive(bytes.fromhex(nonce)).hex()` sent to `AUTH <hex>` → `OK access=engineer`.

2. **Falsified interlock (PROG LIST vs narrative C1-C4)**

- Live: `INTERLOCK_OK = (TANK_TEMP <= 145) AND (TANK_PSI <= 100)`.
- C3 requires `TANK_TEMP <= 45`. The **145** disarmed the temperature limit: the filling would have exceeded 60°C (overtemp abandonment of the bench).
- Correction: `PROG SET INTERLOCK_OK (TANK_TEMP <= 45) AND (TANK_PSI <= 100)`.

3. **Integrity watchdog (keep the fix in place)**

- At arm (`RUNTEST`), if `live_checksum!= trusted_checksum`, the watchdog **restores the backup** and aborts. The backup still contained 145.
- Own solution: `BACKUP SAVE` → backup + trusted reset to the corrected program, `arm_will_restore=0`. (Disabling the watchdog via `WDOG SET enabled=0` also worked, but `BACKUP SAVE` leaves a healthy config.)

4. **Launch**

- `RUNTEST` → `result=SUCCESS reason=fill_target_reached_scan_51` then `flag=...`, `OK compliant`.

5. **Network**

- Hosted instance: TLS routed by SNI. Managed directly in Python: `ssl._create_unverified_context().wrap_socket(sock, server_hostname=HOST)`. No need for the socat tunnel proposed by the README.

## Flag
hiCTF{ground_station_fueling_test_nominal_5fa91a7f13}

## Lessons and reusable patterns
- Validation anchor: diagnostic firmware that prints a signature on a fixed vector is used to confirm a reverse without access to the server. The anchor validates the algorithm, but the live challenge-response depends on the session nonce.
- ARX is recognized by rol/ror + add + xor chained on a few 32-bit words, with the golden constant 0x9e3779b9.
- Safety interlock: looking for a plausible but “too permissive” threshold (145 vs 45) compared to the reference document — this is the typical trap.
- A change is not enough if there is a backup + watchdog: you must update the integrity reference (BACKUP SAVE) or neutralize the watchdog, otherwise the arm restores the old logic.
- Hosted instance = TLS/SNI required: nc in plain text does not connect.
