---
title: "TESSERA"
ctf: "2026-hiCTF"
category: "forensics"
difficulty: "hard"
points: 0
techniques: ["aes-cbc", "xor-cipher", "encoding"]
tools: ["strings", "pycryptodome", "impacket", "python"]
keywords: ["TESSERA", "hiCTF", "forensics", "aes-cbc", "xor-cipher", "encoding", "strings", "pycryptodome", "impacket", "python", "zip", "aes", "base64", "hex", "cbc"]
status: "solved"
has_script: true
source: "hiCTF/Forensics/TESSERA/notes.md"
---

# TESSERA (hiCTF, forensics)

## Summary
Challenge **TESSERA** from the hiCTF CTF, forensics category. Main technique: aes-cbc. “Sub-rosa whispers transversed the local interstice through an unmapped portico… ephemeral colloquy… The prime fracture unbinds the isolated, sightless sanctum, whose lingering phantom subsequently redirects reality itself. » Format hiCTF{part1part2part3}.

## Statement and artefacts
“Sub-rosa whispers transversed the local interstice through an unmapped portico… ephemeral colloquy… The prime fracture unbinds the isolated, sightless sanctum, whose lingering phantom subsequently redirects reality itself. » Format hiCTF{part1part2part3}.

**Provided files / artifacts:**
- `tessera.zip (archive, 992.6 MB)`

## Recognition signals
- Signal: reconstruct a cleaned attack (emptied history and PowerShell logs) from surviving artifacts: registry, slack from an emptied.evtx, ETL, DPAPI, MFT.

## Resolution method
1. **The 3 parts**

| # | Enigma | Artefact | Technique | Raw part |
|---|---|---|---|---|
| 1 | pop-up conference on a local port | `Windows/System32/LogFiles/WMI/AuditDiagTrace.etl` | Provider ETW event `Microsoft-Windows-Diagnostics-LpcEndpoint`: `PORT=\RPC Control\AepLocalEndpoint_Q8;HEX=…`; HEX XORed **0x5A** | `1ist-----hiCTF{alpc_p0rt_c0lloquy_` (+`TargetService:DiagTrackSvcAux`) |
| 2 | isolated and blind sanctuary | Dummy Service `SYSTEM\…\Services\DiagTrackSvcAux\Parameters` → `ServiceVault` = `systemprofile\…\Caches\cpinforev.dat`, `EntropyToken` = Base64(`TesseraEntropy_99`) | **Machine-scoped DPAPI** (session 0 / SYSTEM profile) | `--s32nd--s35s10n_z3r0_syst3npr0f1l3_` (+ `NextKey`, `IV_HEX`, target `ETLLocalStore`) |
| 3 | ghost who “redirects reality” | File `ProgramData\Microsoft\Diagnosis\ETLLocalStore` (MFT 101281) | **NTFS reparse point** (reparse, tag `0xA0000028`, resident in MFT), data in **AES-256-CBC** | `iiiiiiiiiii-3hird---r3p4r53_buff3r_vort3x}` |

Flag = parts after the last group of hyphens: `hiCTF{` + `alpc_p0rt_c0lloquy_` + `s35s10n_z3r0_syst3npr0f1l3_` + `r3p4r53_buff3r_vort3x}`.

2. **Method (chronological)**

| Stage | Command / tool | Result |
|---|---|---|
| 1 | Zip hover (Python `zipfile`) | Complete triage, one real account `N!` |
| 2 | `Security.evtx` → python-evtx (4688) | Only startup processes |
| 3 | Prefetch | `CSC`/`CVTRES` (Add-Type), `MANAGE-BDE`, `VDS`, `REG`, `SC` |
| 4 | `$MFT` → `mft` (Rust/Python), TSV table | Activity window **2026-10-29 ~11:50 UTC**: `ConsoleHost_history.txt` created then **deleted**, `verify_lpc.xml` deleted, `i3zyue5o.cmdline` (resident: compilation `Add-Type`) |
| 5 | NTUSER.DAT + `.LOG1/.LOG2` → `regipy` (`apply_transaction_logs`) | UserAssist: `powershell.exe` launched at 11:49:47 |
| 6 | PowerShell logs | **Clear** (69,632 B = header only, edited at 12:51) |
| 7 | SYSTEM keys changed between 11:49:40 and 11:53 | **`DiagTrackSvcAux`** created at 11:51:08 |
| 8 | `secretsdump.py -system SYSTEM -security SECURITY LOCAL` → `dpapi.py masterkey` → `dpapi.py unprotect -entropy TesseraEntropy_99` | **Part 2** + key/IV/target |
| 9 | 0xC0 attribute of MFT entry `ETLLocalStore` + AES-256-CBC | **Partie 3** |
| 10 | Global search (`T3ss3r4`, `Tessera`…) within 3 GiB | `Microsoft-Windows-PowerShell%4Operational.evtx`'s **slack** contains the **complete script** (ScriptBlock, 3 steps) |
| 11 | `AuditDiagTrace.etl`: UTF-16 string `HEX=…` ⊕ 0x5A | **Part 1** confirmed by the targeted artifact |

## Discarded approaches
- EmptyProxyPort; CustomSDB {22221111-…} = legitimate Microsoft compatibility database.
- WMI (OBJECTS.DATA): only class definitions, no persistence.
- ETW autologger WPR/DiagTrack sessions: legitimate.
- $LogFile, Registry TxR/CLFS logs: noise.
- Contents of non-resident deleted files (verify_lpc.xml,.cs): clusters missing from collection.
- SOFTWARE.LOG1/2 date from 2024: replaying them corrupts the hive -> use the original hive.

## Solve script
Script path: [scripts/solve.py](scripts/solve.py)

## Flag
hiCTF{alpc_p0rt_c0lloquy_s35s10n_z3r0_syst3npr0f1l3_r3p4r53_buff3r_vort3x}

## Lessons and reusable patterns
- Emptying a log (wevtutil cl / Clear-EventLog) does not erase it: the text of old recordings remains in the file -> strings -e l / regex UTF-16 on the.evtx.
- Look for the activity window in the $MFT (creations/deletions), then cross with register (UserAssist, services), Prefetch.
- Add-Type temporary files (.cmdline,.out, RES*.tmp, CSC*.TMP): small, often resident in the MFT even when deleted.
- DPAPI machine offline: SYSTEM (boot key) + SECURITY (DPAPI_SYSTEM) + Protect\S-1-5-18\<GUID>; The master key GUID is in the blob (bytes 24-40). Don't forget the optional entropy.
- NTFS reparse point: stored in the $REPARSE_POINT (0xC0) attribute of the MFT, often resident; an unknown tag = arbitrary data.
- A name that mimics a Windows service (DiagTrack -> DiagTrackSvcAux) created during window = immediate suspect.
- Consider the clock offset (VirtualBox synchronization: −5 h to 11:48) before interpreting the dates.
