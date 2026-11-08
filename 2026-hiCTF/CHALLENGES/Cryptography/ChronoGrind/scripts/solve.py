# ChronoGrind — time-lock puzzle (Rivest-Shamir-Wagner).
#
# state.dat : 'CGD1' + tout le reste XORé avec 0x4C ; après 2 octets d'en-tête,
# des enregistrements TLV : type(1) | longueur(4, little-endian) | données.
#   0x11 anchor (base 241, big-endian) · 0x22 seed (base 241) · 0x33 cycles (décimal)
#   0x44 chk = sha256('anchor:seed:cycles')[:8]
# Calcul : v = seed^(2^cycles) mod anchor  (cycles carrés successifs, non parallélisables)
#          k = sha256(v sur 256 octets big-endian)
# flag.enc : 'CGFX' | ver(1) | nonce(12) | tag(16) | ct  -> ChaCha20-Poly1305
#
# Usage : python3 solve.py <dossier contenant state.dat et flag.enc>
# Reprise : un point de sauvegarde est écrit dans checkpoint.txt tous les 10^8 carrés.
import sys, os, struct, hashlib, functools, time
import gmpy2
from Crypto.Cipher import ChaCha20_Poly1305

D = sys.argv[1]
CKPT = os.path.join(D, 'checkpoint.txt')
STEP = 100_000_000                       # carrés par appel à powmod

# 1) Lire les enregistrements de state.dat
raw = open(os.path.join(D, 'state.dat'), 'rb').read()
x = bytes(b ^ 0x4C for b in raw)
R, p = {}, 6                             # 4 (magic) + 2 (en-tête)
while p + 5 <= len(x):
    t = x[p]; L = struct.unpack('<I', x[p+1:p+5])[0]
    R[t] = x[p+5:p+5+L]; p += 5 + L
b241 = lambda v: functools.reduce(lambda n, b: n * 241 + b, v, 0)
A, S, C = b241(R[0x11]), b241(R[0x22]), int(R[0x33])
assert hashlib.sha256(f'{A}:{S}:{C}'.encode()).digest()[:8] == R[0x44], 'chk invalide'
print(f'anchor {A.bit_length()} bits, cycles = {C}', flush=True)

# 2) Reprise éventuelle depuis le dernier point de sauvegarde
done, v = 0, gmpy2.mpz(S)
if os.path.exists(CKPT):
    d0, v0 = open(CKPT).read().split()
    done, v = int(d0), gmpy2.mpz(v0)
    print(f'reprise à {done} carrés', flush=True)

# 3) Les carrés : powmod(v, 2^n, A) fait exactement n carrés, en C (GMP)
A = gmpy2.mpz(A); t0 = time.time(); start = done
while done < C:
    n = min(STEP, C - done)
    v = gmpy2.powmod(v, gmpy2.mpz(1) << n, A)
    done += n
    with open(CKPT + '.tmp', 'w') as f: f.write(f'{done} {v}')
    os.replace(CKPT + '.tmp', CKPT)      # écriture atomique
    el = time.time() - t0; rate = (done - start) / el
    print(f'{done}/{C} ({100*done/C:.1f} %) — reste ≈ {(C-done)/rate/60:.0f} min', flush=True)

# 4) Clé et déchiffrement (le tag Poly1305 doit être valide)
k = hashlib.sha256(int(v).to_bytes(256, 'big')).digest()
e = open(os.path.join(D, 'flag.enc'), 'rb').read()
assert e[:4] == b'CGFX'
nonce, tag, ct = e[5:17], e[17:33], e[33:]
pt = ChaCha20_Poly1305.new(key=k, nonce=nonce).decrypt_and_verify(ct, tag)
print('FLAG :', pt.decode(), flush=True)
