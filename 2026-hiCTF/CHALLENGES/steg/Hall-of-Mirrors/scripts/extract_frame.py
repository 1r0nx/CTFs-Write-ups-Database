# Extraction MirrorStego v1 (cf. archivist_datasheet.txt section [1])
# Usage: python3 -I extract_frame.py hall-of-mirrors.wav 9C4F1E7A3B50D682 out.bin
import sys, struct, zlib

wav_path, key_hex, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
K = int(key_hex, 16)

# Lecture brute du chunk data (offset 216 etabli dans les notes)
with open(wav_path, 'rb') as f:
    f.seek(216)
    data = f.read()
M = len(data) // 2  # nombre d'echantillons int16 entrelacees

MASK = (1 << 64) - 1
state = K
def sm64():
    global state
    state = (state + 0x9E3779B97F4A7C15) & MASK
    z = state
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & MASK
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & MASK
    return z ^ (z >> 31)

p = -1
def next_bit():
    global p
    p += 1 + (sm64() % 4096)
    if p >= M:
        raise EOFError('depasse la fin du flux')
    w = (sm64() >> 17) & 0xFF
    low = data[2 * p]  # octet bas du int16 LE a l'echantillon p
    return bin(low ^ w).count('1') & 1

def next_bytes(n):
    out = bytearray()
    for _ in range(n):
        b = 0
        for _ in range(8):
            b = (b << 1) | next_bit()  # MSB-first
        out.append(b)
    return bytes(out)

hdr = next_bytes(16)
magic, plen, crc = hdr[:8], struct.unpack('<I', hdr[8:12])[0], struct.unpack('<I', hdr[12:16])[0]
print('magic =', magic, '| payload_len =', plen, '| crc32 =', hex(crc))
assert magic == b'MIRRORS1', 'mauvais magic -> cle ou schema faux'
payload = next_bytes(plen)
ok = zlib.crc32(payload) & 0xFFFFFFFF == crc
print('crc32 payload :', 'OK' if ok else 'ECHEC')
with open(out_path, 'wb') as f:
    f.write(payload)
print('ecrit ->', out_path, '| dernier echantillon visite =', p, '/', M)
