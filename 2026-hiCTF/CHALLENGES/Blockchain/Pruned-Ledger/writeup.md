---
title: "Pruned-Ledger"
ctf: "2026-hiCTF"
category: "blockchain"
difficulty: "Not specified"
points: null
techniques: ["xor-cipher", "blockchain"]
tools: ["pycryptodome", "python"]
keywords: ["Pruned-Ledger", "hiCTF", "blockchain", "xor-cipher", "pycryptodome", "python", "xor", "nonce"]
status: "solved"
has_script: true
source: "hiCTF/Blockchain/Pruned-Ledger/notes.md"
---

# Pruned-Ledger (hiCTF, blockchain)

## Summary
Challenge **Pruned-Ledger** from the hiCTF CTF, blockchain category. Main technique: xor-cipher. A settlement system is decommissioned; the operator deleted fields from the current storage via prune(). The complete archive of the channel remains available. Reconstruct the file box of box 0xca5ef11e.

## Statement and artefacts
a settlement system is decommissioned; the operator deleted fields from the current storage via prune(). The complete archive of the channel remains available. Reconstruct the file box of box 0xca5ef11e. SHA-256 compliant.

**Provided files / artifacts:**
- `pruned-ledger.zip (archive, 67.4 KB)`

## Recognition signals
- Signal: the deleted storage (prune) remains reconstructable from the CALLDATA of the channel archive — nothing is really deleted.
- Signal: prune() only deletes the current storage: the history (calldata of configure/seal) remains in the archive -> total reconstruction. “On-chain deleting ≠ forgetting”.
- Signal: seal stores unmasked in a slot without getter: no need to read the storage, we recalculate the mask from calldata + address(this) + record.
- Signal: Note mask linked to msg.sender: revealable for any offline caller (XOR), simply find the matching by searching for printable ASCII.

## Resolution method
1. **Structure**

- **Relay**: fund hop, immutable `caseTag (bytes4)` + `nextHop`. The `0xca5ef11e` box is a **relay tag**, not a `caseReference`.
- **Ledger**: a file box = 4 fields → `caseReference` (immutable), `record` (`configure`, erased by `prune`), `archive entry` (`seal`, at a derived slot, stored **unmasked**), `note` (revealed by `unlock()` to the only **caller for whom she was spun**, on a bad guess).
- 2 Ledgers deployed: `0xb52e…` (caseRef `archived_state`) and `0x68fb8760…` (caseRef `pruned_storage`).

2. **Resolution channel (100% offline)**

1. Decode the 400 tx legacy (RLP + EIP-155); CREATE addresses = `keccak(rlp[sender, nonce])[12:]`.
2. Decode the **Relay** constructors (`caseTag`, `nextHop`) and follow the trail of the `0xca5ef11e` tag: `0xcaec… → 0xcc08… → 0x137b… → 0x65db… →` **Ledger `0x68fb8760…`** (= the searched box).
3. **record**: only the `configure` of the **operator** count (the others `revert` via `onlyOperator`). The “useful” record = the current one at `seal` = `"calldata"`. (Later random `configure` then `prune` scrambles the final storage, but the calldata keeps everything.)
4. **archive entry** = `maskedEntry(seal) ^ keccak(SEAL_DOMAIN ++ ledger ++ rec_at_seal)` → `"never"`. (`SEAL_DOMAIN = keccak("hictf.pruned-ledger.seal")`.)
5. **note** = `_maskedNote ^ keccak(NOTE_DOMAIN ++ ledger ++ caller)`; we **raw the address** until we obtain ASCII → caller `0x123332…` (= the caller of `unlock`) → `"forgets"`.
6. **caseReference** = `"pruned_storage"`.
7. **Assembly** = subject / adverb / verb / object = caseReference + archive + note + record:
   - `0x68fb8760…` → “**pruned_storage never forgets calldata**”
   - (control parallel) `0xb52e…` → “archived_state always remembers history” The two coherent sentences validate the order and the unmasking model.

3. **Flaws/ideas**

- **`prune()` only deletes the current storage**: the history (calldata of `configure`/`seal`) remains in the archive → total reconstruction. “On-chain deleting ≠ forgetting”.
- **`seal` stores unmasked** in a slot without getter: no need to read the storage, we recalculate the mask from the calldata + `address(this)` + record.
- **Note mask linked to `msg.sender`**: revealable for any offline caller (XOR), simply find the matching by searching for printable ASCII.

## Solve script
Script path: `scripts/solve.py`

## Flag
hiCTF{pruned_storage_calldata_never_forgets}

## Lessons and reusable patterns
- “Pruned” ≠ “disappeared”: on a blockchain, any past write is in the calldata/logs of the archive. Always decode the history rather than just reading the final state.
- A bytes4 in the statement (0xca5ef11e) = often a tag/selector; here the caseTag of a relay track -> identify the terminal contract by following the nextHop.
- Values masked by XOR + domain: entry = masked ^ keccak(DOMAIN ++ address ++ context) — all terms are known offline.
- Validate a reconstruction model on a 2nd case (here the Ledger decoy): two parallel grammatical sentences = proof that the order of the fields is correct.
