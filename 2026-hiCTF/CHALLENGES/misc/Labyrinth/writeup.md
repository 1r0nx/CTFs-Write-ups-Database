---
title: "Labyrinth"
ctf: "2026-hiCTF"
category: "misc"
difficulty: "Not specified"
points: null
techniques: ["xor-cipher", "nx-bypass", "encoding", "wifi"]
tools: ["netcat"]
keywords: ["Labyrinth", "hiCTF", "misc", "xor-cipher", "nx-bypass", "encoding", "wifi", "netcat", "zip", "xor", "hex", "stack", "nonce", "oracle"]
status: "solved"
has_script: false
source: "hiCTF/misc/Labyrinth/notes.md"
---

# Labyrinth (hiCTF, misc)

## Summary
Challenge **Labyrinth** from the hiCTF CTF, misc category. Main technique: xor-cipher. Learn a binary protocol solely by interaction (error messages teach grammar), then map a random maze and respond by the shortest path.

## Statement and artefacts
Not specified.

## Recognition signals
- Signal: learn a binary protocol only by interaction (error messages teach grammar), then map a random maze and respond by the shortest path.
- Signal: Parsing pitfall: binary bytes (token, challenge) can be printable -> don't rely on "where the text starts", but on a fixed marker (ANSWER) or on fixed lengths.

## Resolution method
1. **The “LBY” protocol**

Banner: `LBY\x7f\x80\x00$\x01LABYRINTH speaks in frames. listen.`

**Frame** = `magic(4) | opcode(1) | length(2, big-endian) | payload`
- magic = `LBY\x7f` (the first 4 bytes of the banner; the “bad magic” error says so).
- Server responses have the opcode with the high bit set (0x80, 0x81, 0x90, 0xa0, 0xa1, 0xb0, 0xee, 0xf0).
- `0xee` = error (1st byte of payload = code), `0xf0` = flag (true or decoy).

**Opcode discovery**: send an unknown opcode → `ERR unknown opcode; known: 01 02 10 20 30 40 50 60`.

| opcode | role |
|---|---|
| 0x01 | PROBE → returns an 8 byte nonce |
| 0x02 | STATUS → gives the hint of the current state (does not change state) |
| 0x10 | HELLO → we return the received nonce (`0x10`+nonce) → go to the challenge |
| 0x20 | MOVE in the maze = `dir(1)+token(2)` |
| 0x30 | ANSWER (challenge transform, then labyrinth route) |
| 0x40 | **lure**: `hiCTF{not_the_exit}` |
| 0x50 | **lure**: “debug build stripped. <hex> » |
| 0x60 | **lure**: “warp needs a key you will never have” |

2. **Handshake**

- `0x01` (PROBE) → nonce. `0x10`+nonce (HELLO) → **challenge** (op 0x90).

3. **Challenge “transform” (op 0x90)**

Payload: `03 | 3 pairs (4o input, 4o output) | challenge 4o | "ANSWER T(challenge)"`.
- 1st pair = `00000000 → key` (reveals the 4 byte key, here all equal).
- **Transformation: `T(block) = reverse (key XOR block)`** (inversion of the 4 bytes after XOR). Checked on the other pairs: `01020304 XOR fcfcfcfc = fdfefff8`, inverted = `f8fffefd`. ✓
- Answer `0x30` + `T(challenge)` (**exactly 4 bytes**: the challenge = the 4 bytes just before `ANSWER`, not the example blocks). → entrance to the labyrinth (op 0xa0).
- Bad transform → “wrong transform; the labyrinth forgets you (reset)”: the connection is reset.

4. **Labyrinth (op 0xa0)**

- Cell = `x(1) y(1) exits(1) pad(1) token(2)` [+ text if special].
- **dir = 0..3 = N E S W**; `exits` = `1<<dir` bit mask. Deltas: N=(0,−1), E=(+1,0), S=(0,+1), W=(−1,0).
- MOVE = `0x20` + `dir(1)` + `token(2)` (the token of the current cell). Wrong direction → “wall. token unchanged”.
- **Perfect** maze (tree) and **random at each connection** → everything is done in a single session.
- DFS with backtracking (return = opposite direction `(d+2)%4`), by constructing the graph from the `exits` masks of each visited cell.

5. **The door (op 0xa1)**

- When entering the door: “a sealed gate. it asks how you came, by the shortest way”. The status changes to “ANSWER with the shortest route from the entrance” (we can no longer move).
- BFS input (0,0) → relates to the mapped graph = sequence of directions.
- Submit `0x30` + **raw bytes of directions** (`bytes([d0, d1,...])`). → op 0xf0 = the real flag.

## Flag
hiCTF{l34rn3d_th3_t0ngu3_w4lk3d_th3_l4byr1nth_16988d6da1}

## Lessons and reusable patterns
- Unknown protocol = oracle: forcing errors learns framing (magic, known opcodes), state transitions (“wrong move for this state: <hint>”) and formats (“wants exactly 4 bytes”, “dir must be 0..3”).
- Spot the real verb among the decoys by listing all the opcodes in each state.
- Parsing pitfall: binary bytes (token, challenge) can be printable -> don't rely on "where the text starts", but on a fixed marker (ANSWER) or fixed lengths.
- The 3 example blocks are used to infer the transformation; do not confuse an example output with the challenge.
- “by the shortest way” = BFS, not the DFS path traveled.
- Recognize this type: “a language that no tool knows”, “it answers”, “every answer tells you more” = reverse protocol by interaction.
