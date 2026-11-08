---
title: "Warden’s-Maze"
ctf: "2026-hiCTF"
category: "misc"
difficulty: "hard"
points: null
techniques: ["hash-collision", "pie-bypass", "reverse-engineering"]
tools: ["pwntools", "ghidra", "python"]
keywords: ["Warden’s-Maze", "hiCTF", "misc", "hash-collision", "pie-bypass", "reverse-engineering", "pwntools", "ghidra", "python", "elf", "tcp", "pie"]
status: "solved"
has_script: true
source: "hiCTF/misc/Warden’s-Maze/notes.md"
---

# Warden’s-Maze (hiCTF, misc)

## Summary
Challenge **Warden’s-Maze** from the hiCTF CTF, misc category. Main technique: hash-collision. Pac-Man type game over a TCP/TLS connection; centrally sealed trunk; “a genuine mistake in the engine itself… the visibility code reaches into the map with a hand-rolled index”.

## Statement and artefacts
Pac-Man type game over a TCP/TLS connection; centrally sealed trunk; “a genuine mistake in the engine itself… the visibility code reaches into the map with a hand-rolled index”.

**Provided files / artifacts:**
- `maze-breach.zip (archive, 230.4 KB)`

## Recognition signals
- Signal: 8-bit integer truncation of a “handmade” index in the visibility code -> writes a passable floor over a trunk wall.
- Signal: For each square in the radius dx²+dy² < 0x25 (= 37, so dy goes up to ±6), the function marks the square seen by rewriting the map.
- Signal: The write index is calculated by hand and truncated to int8.
- If we observe For dy=6, dx=0: desired offset +144, think of (int8_t)144 = -112.
- Signal: The writing lands 112 squares before the base instead of 6 lines lower, and copies a value of passable ground there.

## Resolution method
1. **The map (extracted at 0x5e664, string separated by \n)**

21 rows × 24 columns. **Internal** tiles (codes): `#`=1 (wall), `.`=2 (pellet), `=`=3 (vault wall), `-`=4 (vault floor), `*`=5 (price), empty/P/G=0. Display: code1`#`, code2`.`, code3`%`, code4` `, code5`$`, player`@`, warden`G`. Departure `P`=(y1, x12), price `*`=(y11, x11) in the chest, warden `G`=(y19, x11).

2. **Rules (Ghidra decompilation, FUN_00106eca)**

- **Player collision**: feasible if `(tile&0x3f) ≤ 5` AND `(0x35 >> (tile&0x1f)) & 1`. 0x35 = bits {0,2,4,5} → codes **0,2,4,5 usable**; `#`(1) and `=`(3) block. Walk on code 5 (`*`) = **victory** (“The vault is open. You take the prize.”). → Just open **one** `=` tile.
- **Warden**: moves 1 turn out of 2; catches up with you → return to the entrance (score kept). **The modified card persists** through a reset.

3. **The exploit (a single breach)**

- Player in **(y=14, x=4)**: `dy=6` reads the empty square `(y=20, x=4)` (clear vertical view, free column 4), writes to `14*24+4 − 112 = 228` = tile `=` in **(y=9, x=12)** → becomes `0x40` (code 0, passable).
- Then enter from the top: `(8,12) → s (9,12) → s (10,12)- → s (11,12)- → a (11,11)*` = victory.
- Only `(14,4)` writes on index 228 → the wall remains permanently open, even after a reset by the warden.

4. **The bug (FUN_00109680, visibility / “fog of war”)**

For each square in the radius `dx²+dy² < 0x25` (**= 37**, so `dy` goes up to ±6), the function marks the square seen by **rewriting the map**. The write index is calculated by hand and **truncated to int8**:
```
write_index = pr*24 + pc + (int8_t)(dx + 24*dy)
map[write_index] = (tile_lu & 0x3f) | 0x40          #0x40 = “seen” bit; low bits = feasible value
```
For `dy=6, dx=0`: desired offset `+144` → `(int8_t)144 = -112`. The writing lands **112 squares before** the base instead of 6 lines lower, and copies a passable ground value there.

## Solve script
Script path: `scripts/sim.py`
Script path: `scripts/solve.py`

## Flag
hiCTF{maze-warden-vault-seed-2026_c3345cf439}

## Lessons and reusable patterns
- A stripped Rust static-pie binary can still be reverse analyzed: extracting the strings (map, messages) gives the structure; Ghidra headless for logic.
- Look for the “handmade” index: the bug is where the code does not use the safe 2D accessor but calculates an offset by hand -> type truncation (int8/int16), sign, or wrong width.
- Radius: 0x25 = 37, not 25 -> dy reaches ±6, which triggers truncation (24×6=144 > 127).
- Relative OOB writing primitive: if the passable target is a wall, the wall “becomes a floor”.
- Live: the modified card persists through a warden reset -> opening the breach once is enough. Lock the state on the client side (the breach box displays @ when on it).
- Ephemeral instances: the token is mined per instance and is not in the binary; you have to win live, on a live instance.
