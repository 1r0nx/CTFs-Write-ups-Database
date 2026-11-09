---
title: "Dormant-Signer"
ctf: "2026-hiCTF"
category: "blockchain"
difficulty: "Not specified"
points: null
techniques: ["aes-ctr", "xor-cipher", "elliptic-curve", "blockchain"]
tools: ["pycryptodome", "python"]
keywords: ["Dormant-Signer", "hiCTF", "blockchain", "aes-ctr", "xor-cipher", "elliptic-curve", "pycryptodome", "python", "xor", "nonce"]
status: "solved"
has_script: true
source: "hiCTF/Blockchain/Dormant-Signer/notes.md"
---

# Dormant-Signer (hiCTF, blockchain)

## Summary
Challenge **Dormant-Signer** from the hiCTF CTF, blockchain category. Main technique: aes-ctr. A custody office signed withdrawals with an automated off-chain signer; the private key was never recorded; the operator "classified a recovery escrow" and then destroyed the production Authorizer contract. Retrieve the plaintext from the escrow.

## Statement and artefacts
Upon withdrawal (`authorize`), the contract verifies a **co-signature** of the sign on `digest = keccak256(abi_encode(authorizer, request_id, amount, recipient))` (raw, without prefix). Upon decommissioning, the operator **classifies an escrow** via `seal(blob)` or `destroy(final_seal)`:
```
_seal(blob):  masked_secret = blob ^ running_digest           # running_digest = keccak chain of settled digests
docstring  :  filed = escrow ^ escrow_mask(liveness_sig) ^ running_digest
escrow_mask(v,r,s) = keccak256(ESCROW_DOMAIN ++ r ++ s ++ bytes1(v))   # on liveness signature
```
The **liveness signature** = deterministic response from the signer (RFC6979, low-s, v∈{27,28}) on `LIVENESS_DIGEST = keccak256("custody-desk/authorizer/liveness/v1")`, **never submitted on-chain**.

**Provided files / artifacts:**
- `dormant-signer.zip (archive, 73.6 KB)`

## Recognition signals
- Signal: reuse of ECDSA nonce (same r ⇒ same k) -> recovery of the private key of the signer, then reproduction of its deterministic liveness signature (RFC6979, low-s) to remove the mask of an escrow.
- Signal: The operator pre-folded the running_digest in the argument passed to destroy, and _seal folds it a second time ⇒ it DOES NOT cancel.
- Signal: Initially I assumed that blob = escrow ^ mask (running_digest cancels) -> 32 random bytes.
- If we observe the correct model (double folding) makes the escrow readable, remember to validate it on BOTH authorizers.
- If we observe Nonce ECDSA weak/reused on the signing side, think about total leakage of the private key from two signatures on the same r.
- Signal: The security of escrow is entirely based on “only the signer can produce his liveness signature” — false as soon as the key leaks (the liveness signature is deterministic, therefore unique, therefore reproducible).

## Resolution method
1. **Resolution chain**

1. **Decode** the 380 tx legacy (RLP + EIP-155, chainId 7411) offline; find the sender by `ecrecover`. 4 contracts: Notary, VoucherDesk, and **2 Authorizer**:
   - `0x5ebb…`: `authorize×17` + `seal` → **sealed** (decoy).
   - `0xcac5…`: `authorize×23` + `destroy` → **DESTROYED = production**.
2. **Signatures of the signer**: they are in the **calldata** of `authorize` (not at the tx level). Reconstruct each signed `digest` and make `ecrecover` → group by sign. The production sign (`0x4e4bca…`) is attached to the **manufacturer** (tx #52).
3. **Nonce reuse**: multiple pairs share the same `r` (signer's nonce generator is weak — this is NOT RFC6979, verified). Same `r` ⇒ same `k` (the `low-s` makes `k` or `n−k` appear). With two signatures `(r, s₁, z₁)`, `(r, s₂, z₂)`: `k = (z₁−z₂)/(s₁∓s₂)`, then `d = (s₁·k − z₁)/r mod n`. Validated by checking `addr(pubkey)=signer`.
4. **Liveness signature**: with `d`, sign `LIVENESS_DIGEST` in **RFC6979 low-s** (eth_keys == manual impl). → `escrow_mask`.
5. **running_digest exact**: simulate offline `authorize` **successful** (known relay + quota>0 + unused request_id + signature=sign), `rd = keccak(rd ++ digest)` in block order.
6. **Final XOR**: `escrow = final_seal ^ running_digest ^ escrow_mask`.
   - `0xcac5…` (destroyed) → `layout_undead_borrowed_betrays` → **FLAG**.
   - `0x5ebb…` (sealed, decoy) → `packed_frozen_shared_exposes`.

2. **The decipherment model (the trap)**

The operator **pre-folded** the `running_digest` in the argument passed to `destroy`, and `_seal` folds it a **second** time ⇒ it DOES NOT cancel:
```
masked_secret = final_seal ^ running_digest
final_seal    = escrow ^ escrow_mask ^ running_digest
⇒  escrow = final_seal ^ running_digest ^ escrow_mask(liveness_sig)
```
Initially I had assumed that `blob = escrow ^ mask` (running_digest cancels) → 32 random bytes. The correct model (double fold) makes the escrow readable → **validated on BOTH authorizers**.

3. **Source code flaws**

- **Weak/reused ECDSA nonce** on the signing side: total leak of the private key from two signatures to the same `r`.
- The security of escrow is entirely based on “only the signer can produce his liveness signature” — false as soon as the key leaks (the liveness signature is **deterministic**, therefore **unique**, therefore reproducible).

## Solve script
Script path: [scripts/solve.py](scripts/solve.py)

## Flag
hiCTF{layout_undead_borrowed_betrays}

## Lessons and reusable patterns
- Same r on two ECDSA signatures = reused nonce = cooked private key. Always scan for duplicate r (and be careful: low-s can hide a k reused in n−k).
- The off-chain signatures are in the CALLDATA, not in the transaction signature (this is only the relayer's key). Reconstruct the signed digest exactly like the contract (abi_encode, prefix EIP-191 or raw depending on the contract).
- A deterministic signature (RFC6979) is unique: if the key leaks, any “only the signer can produce it” scheme falls away.
- Checking the decryption model on a 2nd case (here the decoy authorizer) removes the ambiguity: a running_digest which “cancels” vs “folds twice” gave random bytes vs readable text.
- Chain replay not necessary: with the signed raw txs we reconstruct the entire deterministic state offline (CREATE addresses = keccak(rlp[sender, nonce])).
