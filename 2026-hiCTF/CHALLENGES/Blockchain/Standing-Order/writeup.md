---
title: "Standing-Order"
ctf: "2026-hiCTF"
category: "blockchain"
difficulty: "Not specified"
points: null
techniques: ["blockchain", "smart-contract", "vm-reverse"]
tools: ["python"]
keywords: ["Standing-Order", "hiCTF", "blockchain", "smart-contract", "vm-reverse", "python", "nonce"]
status: "solved"
has_script: true
source: "hiCTF/Blockchain/Standing-Order/notes.md"
---

# Standing-Order (hiCTF, blockchain)

## Summary
Challenge **Standing-Order** from the hiCTF CTF, blockchain category. Main technique: blockchain. Interaction before effect = reentrancy: search for any call{value} / external transfer placed before the status update (here voucherUsed). acknowledge (sure) serves as a counterexample in the same file.

## Statement and artefacts
- `Attack.sol`: reentrancy contract.
- `exploit.py`: live exploit — `python3 exploit.py <BASE_URL> <info.json>`. Read Setup (disbursement, voucherAmount/Nonce/Signature), compile `Attack` (solcx 0.8.24), deploy **with constructor argument** (Disbursement address), call `go()`, check `isSolved()`. Explicit **legacy** transactions.
- `poc_local.py`: offline reproduction (py-evm) — generates an ephemeral committee key, signs the voucher (EIP-191), deploys `Setup{value:20 ether}`, drains, `isSolved()=true`.

**Provided files / artifacts:**
- `standing-order-player.zip (archive, 4.5 KB)`
- `work/Attack.sol (Solidity contract, 1.0 KB)`

## Recognition signals
- If we observe acknowledge(): voucherUsed[digest]=true before paying, think for sure.
- Signal: disburse(): pays (recipient.call{value:amount}) before voucherUsed[digest]=true -> reentrancy. A single voucher (1 ETH) is replayed in a loop until voucherUsed is placed.
- If you observe Anti-Revert Guard in the attacker, consider only re-entering if the target balance still covers an entire payment.
- Signal: Deployment pitfall: remember to add the ABI-encoded constructor argument to the bytecode when deploying “by hand” (otherwise revert/false state).

## Resolution method
1. Deploy `Attack(disbursement)`.
2. `Attack.go(amount, nonce, sig)` → `disburse(attack, 1 ETH, 0, sig)`.
3. `Attack.receive()` re-enters `disburse` with the **same** voucher as long as `balance(disbursement) >= amount` → 20 payments → reserve at 0.
   - Keep `balance >= amount` essential: otherwise the last `call{value}` fails and `require(ok)` would **revert the whole** chain.

1. **The flaw**

Two reimbursement paths share the **same** signature check, and the digest binds **neither the recipient nor the path**: `voucherDigest = keccak256(abi.encodePacked(amount, nonce))`.
- `acknowledge()`: `voucherUsed[digest]=true` **before** paying → safe.
- `disburse()`: pay (`recipient.call{value:amount}`) **before** `voucherUsed[digest]=true` → **reentrancy**. A single voucher (1 ETH) is replayed in a loop until `voucherUsed` is placed.

## Solve script
Script path: [scripts/exploit.py](scripts/exploit.py)
Script path: [scripts/poc_local.py](scripts/poc_local.py)

## Flag
hiCTF{one_sig_two_paths_then_the_l00p_3e38d3865e}

## Lessons and reusable patterns
- Interaction before effect = reentrancy: search for any call{value} / external transfer placed before the status update (here voucherUsed). acknowledge (sure) serves as a counterexample in the same file.
- A digest that does not bind the context (no recipient, no function selector, no address(this)/chainid) = voucher replayable on any path/recipient.
- Anti-return guard in attacker: only re-enter if the target balance still covers an entire payment.
- Deployment pitfall: remember to add the ABI-encoded constructor argument to the bytecode when deploying “by hand” (otherwise revert/false state).
