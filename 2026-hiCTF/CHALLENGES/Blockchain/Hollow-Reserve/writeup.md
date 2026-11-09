---
title: "Hollow-Reserve"
ctf: "2026-hiCTF"
category: "blockchain"
difficulty: "Not specified"
points: null
techniques: ["blockchain", "reverse-engineering", "vm-reverse"]
tools: ["python"]
keywords: ["Hollow-Reserve", "hiCTF", "blockchain", "reverse-engineering", "vm-reverse", "python", "zip", "oracle"]
status: "solved"
has_script: true
source: "hiCTF/Blockchain/Hollow-Reserve/notes.md"
---

# Hollow-Reserve (hiCTF, blockchain)

## Summary
Challenge **Hollow-Reserve** from the hiCTF CTF, blockchain category. Main technique: blockchain. Oracle = spot price of an AMM -> red flag. If the reference pool is small compared to the amounts loaned, it can be manipulated (especially with a flash loan which cancels the capital cost).

## Statement and artefacts
- `exploit.py`: hard reverse-params + compile `Attack` (solcx 0.8.24), deploy, `pwn(5_000_000e18)`, check `isSolved()`. Prerequisite: `pip install web3 py-solc-x evmole pyevmasm`.

## Recognition signals
- If we observe the price oracle of the facility = spot of a tiny pool (POOL1, think of 100k/1k).
- Signal: Trivially manipulable spot ⇒ overvalued collateral ⇒ massive borrowing.
- Signal: A flash loan provides the capital to pump the pool for the duration of a block.

## Resolution method
1. **Reconstructed system (evmole + pyevmasm)**

- **Vault** `0x267b…`: holds 10,000,000 **RSV** (Reserve Unit token). `a2fb342d(to, amount)` = release, reserved for the facility. Objective: vault < 1,000,000.
- **Facility** `0x2A08…`: `borrow(uint256 collateral, uint256 amount)` (salt `0ecbcdab`) → transferFrom COL, `price=oracle.getPrice()`, `value=price*collateral/1e18`, `maxBorrow=value*7500/10000`, require `amount<=maxBorrow`, then `vault.release(caller, amount)`. `repay(uint256)`.
- **Oracle** `0x0348…`: `getPrice()` (`98d5fdca` salt) = **STATICCALL POOL1.`398482d8()`** = `reserveRSV*1e18/reserveCOL`.
- **POOL1** `0x3c7e…`: AMM UniV2-like **end** (100,000 RSV / 1,000 COL, price 100). Directional swaps: `40f788d2(amountIn, minOut)` = RSV→COL, `dce0772c` = COL→RSV, `a5843f08` = addLiquidity. Reserves packed uint112 in slot0 (low=COL, high=RSV, bit224=flag).
- **COL** `0xAEd0…` “Collateral Unit”, **RSV** `0x2ec9…` “Reserve Unit” (ERC20 standard).
- **MISC** `0x2c21…`: **flash lender ERC-3156** from RSV. `flashLoan(receiver, token, amount, data)` (`5cffe9de`), `maxFlashLoan(token)` (`613255ab`) = 5,000,000, `flashFee` (`d9d98ce4`) = 0. Callback `onFlashLoan(address, address, uint256, uint256, bytes)` (`23e30c8b`) should return `keccak256("ERC3156FlashBorrower.onFlashLoan")` = `0x439148f0…`, then the lender does `transferFrom(receiver, lender, amount+fee)`.

2. **Exploit (atomic, in onFlashLoan)**

1. `MISC.flashLoan(this, RSV, 5_000_000e18, "")`.
2. `POOL1.40f788d2(5_000_000e18, 0)`: swap all RSV → COL. Reserve COL from POOL1 → ~20 ⇒ **price ~260,000×1e18**, and I receive ~980 COL.
3. `FAC.borrow(colBalance, vaultRSVBalance)`: collateral valued ~255M ⇒ I borrow **the entire** vault reserve (10M).
4. `approve(MISC, amount)` → the lender recovers 5M. Vault → 0. `isSolved()=true`.

3. **Reverse — method (reproducible)**

1. `/info` → Setup; read its getters (`vault`, `facility`, `player`, constants `pure`).
2. `evmole.contract_info(bytecode)` → selectors + arg types + mutability + layout storage.
3. **Call the getters `pure`** = read the constants (addresses of tokens/pools/oracle, LTV, price, etc.).
4. `pyevmasm` to disassemble; **warning**: solc 0.8.24 emits `PUSH0` (0x5f) which old disassemblers display “INVALID”.
5. **Decode revert strings** (PUSH-string) to guess semantics (“pool: slippage/zero” ⇒ AMM `swap(amountIn, minOut)`).
6. Recognize the ERC-3156 by the callback selector `0x23e30c8b` and the magic `0x439148f0…`.

4. **The flaw**

The price oracle of the facility = **spot of a tiny pool** (POOL1: 100k/1k). Trivially manipulable spot ⇒ overvalued collateral ⇒ massive borrowing. A **flash loan** provides the capital to pump the pool for the duration of a block.

## Solve script
Script path: [scripts/exploit.py](scripts/exploit.py)

## Flag
hiCTF{th1n_p00l_was_the_r3al_0racle}

## Lessons and reusable patterns
- Oracle = spot price of an AMM -> red flag. If the reference pool is small compared to the amounts loaned, it can be manipulated (especially with a flash loan which cancels the capital cost).
- A fee-free flash loan + spot oracle = classic reserve emptying recipe.
- Reverse without sources: evmole (signatures/args/storage) + call of pure getters (constants) + revert chains are enough to reconstruct the logic; no need for a perfect decompiler.
- Think about PUSH0 (solc ≥0.8.20, evm “shanghai/cancun”) when a disassembler shows inconsistent “INVALIDs”.
