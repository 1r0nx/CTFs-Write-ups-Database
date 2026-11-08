---
title: "Cold-Chain"
ctf: "2026-hiCTF"
category: "hardware"
difficulty: "Not specified"
points: null
techniques: ["log-analysis", "hardware", "ot-ics"]
tools: ["python"]
keywords: ["Cold-Chain", "hiCTF", "hardware", "log-analysis", "ot-ics", "python", "nonce"]
status: "solved"
has_script: true
source: "hiCTF/hardware/Cold-Chain/notes.md"
---

# Cold-Chain (hiCTF, hardware)

## Summary
Challenge **Cold-Chain** from the hiCTF CTF, hardware category. Main technique: log-analysis. ColdLink CaseManager CM-900 Refrigeration Controller. All boxes are blocked in continuous defrost; you must authenticate, find the cause, bring the 6 boxes below the compliance ceiling (5°C) and keep them there for 60 s. “a naive fix doesn’t stick” -> the real cause persists.

## Statement and artefacts
ColdLink CaseManager CM-900 refrigeration controller. All boxes are blocked in continuous defrost; you must authenticate, find the cause, bring the 6 boxes below the compliance ceiling (5°C) and keep them there for 60 s. “a naive fix doesn't stick” -> the real cause persists.

**Provided files / artifacts:**
- `cold-chain.zip (archive, 6.4 KB)`
- `work/CLMP_reference.md (text, 6.0 KB)`
- `work/README.txt (text, 2.4 KB)`
- `work/historian_sample.log (text, 982 B)`

## Recognition signals
- If we look at ICS/SCADA, think about persistence automation.
- Signal: An S9 schedule force_defrost forces defrost; the **M2 macro ensure_schedule (period=90s, target=S9) constantly reactivates it**.
- Signal: Deleting/deactivating S9 alone does not work (the macro restores it in ≤90 s).
- Signal: Fix = disable M2 first, then disable S9.

## Resolution method
1. **Auth CLMP**: greeting `SERIAL` + `NONCE`, response `AUTH <serial> <token>` with `token = sha256("CLNK-FIELD-MASTER-6E1D-DO-NOT-DISTRIBUTE|serial|nonce").hexdigest()[:16]` (clear master key in `coldlink_tech.py:auth_token()`). → `OK role=technician`.
2. **Recon**: `CASES` (6 boxes at 12°C, mode=defrost), `SCHED LIST` (S1/S3 cool_all **on**, **S9 force_defrost on**), `MACRO LIST` (M1 noop, **M2 ensure_schedule period=90 → target S9**), `STATUS` (`reason=forced_defrost_schedule_active, cases_above_5C=6, persistence_macro_enabled`). The historian confirms: `macro_apply macro=M2 schedule=S9 detail=re-enabled_forced_defrost` every 90 s.
3. **Fix (important order)**:
   - `MACRO DISABLE M2` → stops persistence.
   - `SCHED SET S9 enabled=0` → neutralizes the forcing (S1/S3 cool_all then cools towards the 2 °C setpoint).
4. **Hold**: Monitor `STATUS`/`CASES` on a maintained connection. tmax 12 → ~2.3 °C; `held` rises 0→64 s; at 60 s → `compliant=1` + `DATA flag=hiCTF{...}`.

1. **Key concept**

**ICS/SCADA: persistence automation.** A `S9 force_defrost` schedule forces defrost; the **macro M2 `ensure_schedule` (period=90s, target=S9)** **reactivates** it constantly. Deleting/deactivating S9 alone does not work (the macro restores it in ≤90 s). Fix = **disable M2 first**, then disable S9.

## Solve script
Script path: `scripts/clmp.py`
Script path: `scripts/coldlink_tech.py`
Script path: `scripts/solve.py`

## Flag
hiCTF{cold_chain_restored_defrost_cleared_ee8e33bfcc}

## Lessons and reusable patterns
- Recognize: “it comes back on its own” after a manual fix = basic automation (macro/timer) which
- Order: disable persistence before the symptom, otherwise the fix is canceled in the timer window.
- Ceiling 5°C, maintenance window 60 s: you have to hold, not just cross once (polling on a
- Auth key: fleet master key hardcoded in the toolkit (classic ICS anti-pattern).
- SCHED DEL S9 would also work but enabled=0 is enough once M2 is cut; MODE <case> cool alone does not hold
