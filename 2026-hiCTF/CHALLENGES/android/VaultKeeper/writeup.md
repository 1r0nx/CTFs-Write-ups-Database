---
title: "VaultKeeper"
ctf: "2026-hiCTF"
category: "android"
difficulty: "hard"
points: null
techniques: ["xor-cipher", "reverse-engineering", "android-reverse", "git-forensics", "vm-reverse"]
tools: ["radare2", "objdump", "strings", "jadx", "apktool", "frida"]
keywords: ["VaultKeeper", "hiCTF", "android", "xor-cipher", "reverse-engineering", "android-reverse", "git-forensics", "vm-reverse", "radare2", "objdump", "strings", "jadx", "apktool", "frida", "apk", "xor"]
status: "solved"
has_script: false
source: "hiCTF/android/VaultKeeper/notes.md"
---

# VaultKeeper (hiCTF, android)

## Summary
Challenge **VaultKeeper** from the hiCTF CTF, android category. Main technique: xor-cipher. (validated by the native tag: SHA256("VK-TAG-2026" || flag)[:16] == 62672db1…)

## Statement and artefacts
(validated by the native tag: SHA256("VK-TAG-2026" || flag)[:16] == 62672db1…)

**Provided files / artifacts:**
- `VaultKeeper.apk (application Android, 4.5 MB)`
- `VaultKeeper.apk.jadx (file, 3.2 KB)`
- `VaultKeeper.zip (archive, 3.5 MB)`

## Recognition signals
- Signal: Lots of hiCTF{} lures (rodata, honeypot functions, logcat). Validate only with the SHA tag.
- Signal: random armToken = irrelevant (derivation only depends on vault.bin).
- If you observe Unicorn Emulation, consider enabling SSE + Haswell CPU model (SHA uses pshufb/SSSE3/SSE4).
- If we observe Check the jumptable to the nearest byte, thinking about an index offset distorts the entire ISA.
- Signal: The prog is 2048 bytes (do not truncate it because of the return 0 from nvUnseal).

## Resolution method
1. **Overview**

Kotlin APK + native lib `libvaultnative.so` (arm64 + x86_64). The “claim” flow (a button, after an arming gesture): `nvSeed → CellMixer.k1 → nvUnseal → CellMixer.k2 → nvExec → nvFinal`. The flag is **never displayed**: it is assembled internally by `nvFinal`, validated by an SHA tag, then **deleted**. All analysis is **static** (anti-debug/anti-frida/anti-root in `EnvAudit` → `noteManagedFault`). The `armToken` (gesture) is a **SecureRandom** → with no effect on the result (cells/prog/VM depend on it via consistency checks only; the derivation is deterministic).

2. **Pipeline (all deterministic from assets/vault.bin)**

1. **nvSeed** (native): `cells[128]` (int32 LE) =
   - `seed = SHA256custom(vault || "VK-SEED-v1")` then `cells[i] = SHA256custom(seed || i_le32)` (16×32 B).
   - **SHA-256 to IV custom**: standard K constants (rodata 0x3230), **IV = 32 bytes @0xeb0‖0xe80** interpreted as **8 little-endian words** (the visible “decoy” was only in the.so arm64).
2. **k1** (Kotlin, in-place): 7 passes on the 128 cells, `rotl/rotr`, `MUL_C = -0x7a143595`, mask `&0x7f`.
3. **nvUnseal** (native): `prog[2048] = cells[(7+i·0x1f)&0x7f] >> ((i&3)·8) ^ ks5f50[i%51] ^ const[0xf60+i] ^ 0xA5`. `ks5f50` = deterministic keystream of `sub_5f50` (SHA on rodata `0x2220` + "VK-SELFMIX-v1", without token).
4. **k2** (Kotlin): XOR by keystream derived from cells, in blocks of 256. Gives the **bytecode** of the VM.
5. **nvExec** (native): executes the bytecode in a **registered VM** (see ISA below). Output = `M[0..15]` (64 bytes) copied to global `8cb0`.
6. **nvFinal** (native): if `fault==0`, assemble `flag[i] = const1[0x1770] ^ const2[0x17b0] ^ 8cb0 ^ ks5f50` (51 bytes), **check** `SHA256("VK-TAG-2026"||flag)[:16] == tag@0x17f0`, otherwise decoy path.

3. **The VM (nvExec) — the heart of the challenge**

- 8 registers `R0..R7` (int32), memory `M[128]` words (ctx+0x20, also byte addressable), output counter `ctx+0x320` (init 0x40), comparison flag `ctx+0x324`, cells pointer `ctx+0x328`.
- **Jumptable @0x1814** (30 opcodes). ISA rebuilt: `0`=NOP, `1`=LOADI reg, imm32, `2/3/4/5`=LOAD/STORE W/B, `6-16,20`=ALU reg-reg (MOV, ADD, SUB, MUL, XOR, AND, OR, SHL, SHR, ROL, ROR + CMP via subjumptable @0x188c), `17`=LOADCELL reg = **byteswap**(cells[idx]), `18`=JMP, `19`=JNZ, `21`=Jcmp, `22`=OUTPUT, `23`=readback, `24`=DJNZ reg, target, `25`=**MIX** `reg=rol(Rc,27)^rol(Ra+reg,7)`, `26`=LOADM, `27`=HALT(ret0), `28`=LOADMR, `29`=STOREM.
- **Time-lock**: `LOADI R7, 0x05F5E100` (= **100,000,000**) then a loop `3×MIX(R0, R1, R2) + DJNZ R7` → **400 million VM instructions**. Anti-emulation: Unicorn (performed) is too slow/unstable; the right approach is to **reimplement the VM in C** (see `work/vm.c`), which does the 400M steps in <1 s.

4. **Solve method (reproducible)**

1. `jadx`/`apktool` for Kotlin + smali (check k1/k2 at smali, not at decompilation).
2. `objdump -d` on the `.so` x86_64 for nv_seed/unseal/exec/final + the VM.
3. Emulate nv_seed (Unicorn x86_64, Haswell, SSE) → cells; **check** them against a SHA-256-IV-custom reimplementation in Python (all 128 must match).
4. Reimplement k1, nvUnseal, k2 in Python (nvUnseal **checked** byte-to-byte against emulation).
5. Reimplement the **VM in C** (`work/vm.c`); validate the first 16 steps against a Unicorn trace (registers), then execute the 400M steps → `8cb0 = M[0..15]`.
6. `flag = const1 ^ const2 ^ 8cb0 ^ ks5f50`; **validate the tag** `SHA256("VK-TAG-2026"||flag)[:16]`.

5. **Final assembly (Python)**

```python
# 8cb0 comes from VM C; const1/const2/tag of the rodata; ks5f50 taken from sub_5f50
flag=bytes((const1[i]^const2[i]^cb[i]^ks51[i])&0xff for i in range(51))
assert hashlib.sha256(b"VK-TAG-2026"+flag).digest()[:16]==exp_tag   #-> True
# flag = hiCTF{!!I_10v3_4ndr0!d_m4n_m4k!ng_th3m_f331_g0Od!!}
```

6. **Pitfalls encountered**

- **Lots of lures** `hiCTF{}` (rodata, honeypot functions, logcat). Validate only with the **SHA tag**.
- Random `armToken` = **irrelevant** (the derivation only depends on `vault.bin`).
- Unicorn emulation: enable SSE + **Haswell** CPU model (SHA uses `pshufb`/SSSE3/SSE4); the **timing** check in nvExec imposes a clock whose deviation falls in `[400 ms, 14488 ms]`; anti-tamper checks must pass (`fault==0`) otherwise decoy path.
- **Check the jumptable to the nearest byte**: an index offset distorts the entire ISA.
- The `prog` is **2048 bytes** (do not truncate it because nvUnseal returns 0).

## Flag
hiCTF{!!I_10v3_4ndr0!d_m4n_m4k!ng_th3m_f331_g0Od!!}

## Lessons and reusable patterns
- Typical “hard” Android channel: fine Kotlin (already readable) + all the secret natively, with a
- Recognize: System.loadLibrary, native methods, anti-frida/anti-debug, lots of false flags.
- Winning reflex: emulate heavy primitives (SHA) under Unicorn, but port the hot VM to C,
- The real flag is the one that passes the integrity tag, never a hiCTF{} found by strings.
