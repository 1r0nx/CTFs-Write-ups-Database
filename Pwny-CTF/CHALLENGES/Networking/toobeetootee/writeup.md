---
title: "toobeetootee"
ctf: "Pwny-CTF"
category: "network"
difficulty: "hard"
points: null
techniques: ["pcap-analysis"]
tools: ["wireshark", "tshark", "python"]
keywords: ["toobeetootee", "Pwny-CTF", "network", "pcap-analysis", "wireshark", "tshark", "python", "pcap", "zip", "png", "https"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Networking/toobeetootee/notes.md"
---

# toobeetootee (Pwny-CTF, network)

## Summary
Challenge **toobeetootee** from the Pwny-CTF CTF, network category. Main technique: pcap-analysis. The toobeetootee challenge (Pwny-CTF, network) is documented by a resolution note.

## Statement and artefacts
“toobeetootee” = **2b2t**; **popbob** (griefer) broke flag blocks. `world.zip` = damaged state (nothing readable), but the **pcap** contains the original state.

**Provided files / artifacts:**
- `toobeetootee.pcap (network capture, 3.2 MB)`
- `world.png (image, 176.5 KB)`
- `world.zip (archive, 7.2 MB)`
- `work/flag_clean.png (image, 935 B)`
- `work/flag_final.png (image, 1.1 KB)`
- `work/flag_full_mirror.png (image, 1.1 KB)`
- `work/flag_h1.png (image, 2.2 KB)`
- `work/flag_h2.png (image, 2.1 KB)`
- `work/flag_mirror.png (image, 1.2 KB)`
- `work/flag_normal.png (image, 1.2 KB)`
- `work/flag_restored.png (image, 940 B)`
- `work/parsed.pkl (file, 13.4 MB)`
- `work/s2c.hex (file, 2.6 MB)`

## Recognition signals
- Signal: Unknown protocol -> parse it yourself: framing, reassembly of fragments, decompression.
- Signal: world.zip = grieved final state; the original is reconstructed from the pcap (BLOCKDATA = complete state sent on loading, before edits).
- Signal: Trap 1 (X superposition): the flag node existed on several X planes (facade + house). Overwriting all the
- Signal: Trap 2 (grievance holes): the blocks loaded after the grievance are missing nodes -> restore the REMOVENODE positions (they were from the flag) to complete the letters (eg the initial B).
- If we observe Trap 3 (mirror): a wall can be read upright on one side only, remember to test the inversion of the axis.

## Resolution method
1. **Mapping** — `tshark -q -z io, phs`: 100% UDP traffic `data` = **Minetest** (not decoded by tshark). Server `192.168.1.201:30000`, signature `4f457403`.
2. **Parse the protocol** (`solve.py`): framing `proto(4)+peer_id(2)+channel(1)` then packet `CONTROL/ORIGINAL/SPLIT/RELIABLE`. Unpack the `RELIABLE (0x03)` and **reassemble the `SPLIT (0x02)`** by `(channel, seqnum)`.
3. **Count commands** server→client: `BLOCKDATA (0x20)` ×2750, `REMOVENODE (0x22)` ×275, `ADDNODE (0x21)` = 0 → popbob only **broke** blocks.
4. **Decode BLOCKDATA**: position `(X, Y, Z)` + serialized MapBlock → decompression **zlib** → array `param0` (4096 content-ids). Keep the **1st state seen** per block (= before complaint). Air = id **126**.
5. **Find the flag material**: original content-id at positions `REMOVENODE` → **id 54** (the flag is written with this node).
6. **Rebuild**: `solid = {nodes id54} ∪ {positions REMOVENODE}` (popbob broke flag nodes → restore them fills the holes). Isolate the **facade** (plane `X = -357`) to avoid superposition of layers (house), then **project onto Y-Z** (inverted Z = reading right side up).
7. **Rendering**: mini PNG encoder in pure Python (no PIL), reading glyph by glyph.

1. **More difficult variation**

- **Encrypted** protocol (recent versions / TLS) → the keys are required.
- Flag in **steganography** in a texture rather than in blocks.
- Several node materials/colors to encode the flag → manage the content-id ↔ name mapping (package `NODEDEF 0x3a`).

2. **References (Minetest/Luanti protocol)**

The source of truth is the **Minetest/Luanti source code**:
- `src/network/networkprotocol.h` — command identifiers and packet types:
  - `PROTOCOL_ID = 0x4f457403`
  - packet types: `CONTROL 0x00`, `ORIGINAL 0x01`, `SPLIT 0x02`, `RELIABLE 0x03`
  - server→client commands: `TOCLIENT_BLOCKDATA 0x20`, `TOCLIENT_ADDNODE 0x21`, `TOCLIENT_REMOVENODE 0x22`
- `src/mapblock.cpp` (`MapBlock::serialize`) and `src/mapnode.cpp` (`MapNode::serializeBulk`) — serialization of a MapBlock (version, flags, `content_width`/`params_width`, zlib stream, order `param0`/`param1`/`param2`); air content-id = **126**.
- Deposit: https://github.com/luanti-org/luanti (ex-`minetest/minetest`).
- Wiki dev (prose): https://dev.minetest.net → *Network Protocol* and *Map serialization format* sections.

> Method actually used here: knowledge of the format above **+ empirical verification** on the bytes (signature `4f457403`, search for the zlib header `78 9c` giving 16384 decompressed bytes).

3. **To remember / pitfalls**

- **Unknown protocol** → parse it yourself: framing, reassembly of fragments, decompression.
- **`world.zip` = grieved final state**; the original is reconstructed from the pcap (BLOCKDATA = complete state sent on loading, before edits).
- **Trap 1 (X superposition)**: the flag node existed on several X planes (facade + house). Overwriting all the
- **Trap 2 (grievance holes)**: the blocks loaded *after* the grievance are missing nodes → **restore the `REMOVENODE` positions** (they were from the flag) to complete the letters (e.g. the initial `B`).
- **Trap 3 (mirror)**: a wall can be read upright on one side only → test the inversion of the axis.

## Solve script
Script path: `scripts/solve.py`

## Flag
uiuctf{BudG3t_c4ves_N_cl1fFs}

## Lessons and reusable patterns
- Main technique: pcap-analysis.
