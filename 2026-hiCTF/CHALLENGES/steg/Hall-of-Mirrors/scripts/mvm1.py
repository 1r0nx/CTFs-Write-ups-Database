# Emulateur MVM1 (cf. archivist_datasheet.txt section [2])
# Usage: python3 -I mvm1.py payload.bin out_vm.bin
import sys

img = open(sys.argv[1], 'rb').read()
assert img[:4] == b'MVM1'
code_len = int.from_bytes(img[4:8], 'little')
data_len = int.from_bytes(img[8:12], 'little')
entry = int.from_bytes(img[12:14], 'little')
CODE = bytearray(0x10000); CODE[:code_len] = img[16:16 + code_len]
DATA = bytearray(0x10000); DATA[:data_len] = img[16 + code_len:16 + code_len + data_len]

M = (1 << 64) - 1
R = [0] * 16
R[15] = 0xCBF29CE484222325
stack = []
pc = entry
out = bytearray()
rotl = lambda v, n: ((v << n) | (v >> (64 - n))) & M if n else v

steps = 0
while True:
    steps += 1
    if steps > 200_000_000:
        raise RuntimeError('trop long')
    op = CODE[pc]
    # hash anti-tamper sur CHAQUE fetch, avant decode/exec
    R[15] = ((R[15] ^ op) * 0x100000001B3) & M
    R[15] ^= R[15] >> 31
    if op == 0x6E: pc += 1                                   # NOP
    elif op == 0x3A:                                         # IMM
        r = CODE[pc+1] & 0xF
        R[r] = int.from_bytes(CODE[pc+2:pc+10], 'little'); pc += 10
    elif op == 0xD1:
        b = CODE[pc+1]; R[b >> 4] = R[b & 0xF]; pc += 2      # MOV
    elif op == 0x95:
        b = CODE[pc+1]; R[b >> 4] = DATA[R[b & 0xF] & 0xFFFF]; pc += 2   # LDB
    elif op == 0x4C:
        b = CODE[pc+1]; DATA[R[b >> 4] & 0xFFFF] = R[b & 0xF] & 0xFF; pc += 2  # STB
    elif op == 0x27:                                         # LDQ
        b = CODE[pc+1]; a = R[b & 0xF] & 0xFFFF
        R[b >> 4] = int.from_bytes(bytes(DATA[a:a+8]), 'little'); pc += 2
    elif op == 0xB8:                                         # STQ
        b = CODE[pc+1]; a = R[b >> 4] & 0xFFFF
        DATA[a:a+8] = (R[b & 0xF]).to_bytes(8, 'little'); pc += 2
    elif op == 0x6A:
        b = CODE[pc+1]; R[b >> 4] = CODE[R[b & 0xF] & 0xFFFF]; pc += 2   # LDC
    elif op == 0x7F:
        b = CODE[pc+1]; R[b >> 4] = (R[b >> 4] + R[b & 0xF]) & M; pc += 2
    elif op == 0xE3:
        b = CODE[pc+1]; R[b >> 4] = (R[b >> 4] - R[b & 0xF]) & M; pc += 2
    elif op == 0x12:
        b = CODE[pc+1]; R[b >> 4] = (R[b >> 4] * R[b & 0xF]) & M; pc += 2
    elif op == 0xA6:
        b = CODE[pc+1]; R[b >> 4] ^= R[b & 0xF]; pc += 2
    elif op == 0x5B:
        b = CODE[pc+1]; R[b >> 4] &= R[b & 0xF]; pc += 2
    elif op == 0xCC:
        b = CODE[pc+1]; R[b >> 4] |= R[b & 0xF]; pc += 2
    elif op == 0x39:
        r = CODE[pc+1] & 0xF; R[r] = (R[r] << (CODE[pc+2] & 63)) & M; pc += 3
    elif op == 0x8D:
        r = CODE[pc+1] & 0xF; R[r] >>= (CODE[pc+2] & 63); pc += 3
    elif op == 0x61:
        r = CODE[pc+1] & 0xF; R[r] = rotl(R[r], CODE[pc+2] & 63); pc += 3
    elif op == 0xF2: pc = int.from_bytes(CODE[pc+1:pc+3], 'little')      # JMP
    elif op == 0x1D:                                         # JZ
        r = CODE[pc+1] & 0xF; t = int.from_bytes(CODE[pc+2:pc+4], 'little')
        pc = t if R[r] == 0 else pc + 4
    elif op == 0xC4:                                         # JNZ
        r = CODE[pc+1] & 0xF; t = int.from_bytes(CODE[pc+2:pc+4], 'little')
        pc = t if R[r] != 0 else pc + 4
    elif op == 0x50:                                         # JLT (non signe)
        b = CODE[pc+1]; t = int.from_bytes(CODE[pc+2:pc+4], 'little')
        pc = t if R[b >> 4] < R[b & 0xF] else pc + 4
    elif op == 0x9A:
        stack.append(pc + 3); pc = int.from_bytes(CODE[pc+1:pc+3], 'little')  # CALL
    elif op == 0x2E: pc = stack.pop()                        # RET
    elif op == 0xB3:
        out.append(R[CODE[pc+1] & 0xF] & 0xFF); pc += 2      # OUT
    elif op == 0xE8:
        b = CODE[pc+1]; CODE[R[b >> 4] & 0xFFFF] = R[b & 0xF] & 0xFF; pc += 2  # PCH
    elif op == 0x74:
        r = CODE[pc+1] & 0xF; R[r] = (~R[r]) & M; pc += 2    # NOT
    elif op == 0x47:                                         # SMC auto-dechiffrement
        b = CODE[pc+1]; ln = int.from_bytes(CODE[pc+2:pc+4], 'little') or 0x10000
        seed = (R[b & 0xF] ^ R[15]) & M
        x = seed if seed else 0x9E3779B97F4A7C15
        base = R[b >> 4]
        for i in range(ln):
            x ^= (x << 13) & M; x ^= x >> 7; x ^= (x << 17) & M
            CODE[(base + i) & 0xFFFF] ^= (x >> 24) & 0xFF
        pc += 4
    elif op == 0x0B: break                                   # HLT
    else:
        raise RuntimeError(f'opcode inconnu {op:02X} @ {pc:04X} (step {steps})')

sys.stderr.write(f'HLT apres {steps} instructions, {len(out)} octets emis\n')
open(sys.argv[2], 'wb').write(bytes(out))
