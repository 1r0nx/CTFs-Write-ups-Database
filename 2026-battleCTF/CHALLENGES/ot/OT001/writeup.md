---
title: "OT001"
ctf: "2026-battleCTF"
category: "ot"
difficulty: "Not specified"
points: 45
techniques: ["modbus", "ot-ics"]
tools: ["python"]
keywords: ["OT001", "battleCTF", "ot", "modbus", "ot-ics", "python", "tcp", "https"]
status: "solved"
has_script: true
source: "battleCTF/CHALLENGES/ot/OT001/notes.md"
---

# OT001 (battleCTF, ot)

## Summary
Challenge **OT001** from the battleCTF CTF, ot category. Main technique: modbus. The registers of an automaton. “Security” (setpoint ceiling) is only applied to single writing (FC06) and is bypassed by multiple writing (FC16).

## Statement and artefacts
This is a small water treatment plant's dosing controller, reachable directly over the network.

INCIDENTS:

In February 2021, an operator at the Oldsmar, Florida water treatment plant watched their mouse move on its own and saw the sodium hydroxide (lye) setpoint jump from 100ppm to 11,100ppm, changed remotely by an unknown party, then caught and reverted before it reached the water supply.

In November 2023, the "CyberAv3ngers" group compromised Unitronics PLCs running water booster stations across the US and Israel, reachable directly from the internet with no meaningful access control. Neither incident involved a memory-corruption exploit. Both came down to the same thing: the protocol let anyone with network access change whatever they wanted.

https://otctf.pages.dev/water-treatment/

- Soda (NaOH) dosing station of a water plant, controlled by **Modbus TCP** on `169.58.126.107:6000`.
- No code, no binary, no register map provided: **everything is discovered by talking to the endpoint**.
- Objective: to cause a **dangerous and sustained overdose**. The flag is inert data which is **published only once the factory is truly in a dangerous state**.

**Provided files / artifacts:**
- `work/modbux-2.3.0-x86_64.AppImage (file, 126.9 MB)`
- `work/water-treatment (file, 13.6 KB)`

## Recognition signals
- Signal: Anyone on the network can read/write.
- If we observe classic trap/flaw, think about a validation placed only on FC06 (write single) se.

## Resolution method
1. **Map of registers (discovered by sampling) - all in HOLDING REGISTERS**

| reg | role | remarque |
|-----|------|----------|
| [0] | **NaOH setpoint** (setpoint) | writable; FC06 **rejects any value > 200** (rereads 0) |
| [1] | **measured concentration** | driven by the process, **progressively rises towards [0]** |
| [2] | **danger indicator** | goes to 1 when the setpoint becomes dangerous |
| [3] | status bit | =1 at rest |
| 100..118 | **the flag** | published in ASCII (2 characters/register) when [1] exceeds ~9600 |

Coils / input registers / discrete inputs → **error** (not implemented). Everything is in holding.

1. **Recon reading** — `read_holding_registers(0,40)`: everything at 0 except `[3]=1`, nothing moves alone → the factory is at rest, it must be controlled by writing**.
2. **Probe by writing** — write a reg witness value by reg + read again:
   - writing [0] makes **react [1]** → [0]=input (setpoint), [1]=output (measurement).
   - [1] written directly is **rewritten by the process** → it is a measurement, not an adjustment.
3. **Range of [0]** — scan: [0] only accepts **0..200** in FC06 (≥255 → rejected, reread 0). The concentration [1] **tends towards [0]** with a delay (1st order dynamics).
4. **Bypass (the core)** — `write_registers(0,[11100,0])` (**FC16**): [0] rereads **11100**, the validation of FC06 is **bypassed**. [2] goes to 1 (armed danger).
5. **Hold** — keep [0]=11100; [1] climbs (a few seconds → ~9600).
6. **Flag** — as soon as [1] > ~9600, read the holding registers **100..118** and **decode in ASCII** (each 16-bit register = 2 bytes) → `CTF{...}`.

2. **How to redo it in modbux (GUI)**

- Connection: **Modbus TCP**, IP `169.58.126.107`, port `6000`, **Unit/Slave ID = 1**.
- Read **Holding Registers** 0..40 to observe (we see [3]=1).
- Write the instruction: use **Write Multiple Registers (FC16)** on addresses **0-1** with the values ​​`11100, 0`. (Write Single Register / FC06 at 11100 would be **rejected** → capped at 200.)
- Read **Holding Registers 100..120** and change the display to **ASCII/String**: the flag is displayed once the concentration ([1]) rises above ~9600.

## Solve script
Script path: [scripts/solve.py](scripts/solve.py)

## Flag
CTF{a95d4db0158d93bbe8d3290b503e7437}

## Lessons and reusable patterns
- OT/ICS = no auth by design. The vulnerability is not a memory corruption: it is that
- Modbus discovery reflex: read the 4 zones (coils, discrete, input/holding regs); spot
- Classic trap/flaw: validation placed only on FC06 (write single)
- Flag in registers: 1 register = 16 bits = 2 ASCII characters (big-endian) -> decode a range
- Value 11100 = nod to Oldsmar (lye 100 -> 11,100 ppm).
- Script: work/solve.py.
