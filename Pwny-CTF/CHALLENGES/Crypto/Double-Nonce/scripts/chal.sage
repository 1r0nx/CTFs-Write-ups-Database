# Double-Nonce — Pwny-CTF (script de solve)
import hashlib
import json
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

# Curve Setup: secp256k1 
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
a = 0
b = 7
E = EllipticCurve(GF(p), [a, b])
Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
G = E(Gx, Gy)
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Generate a random private key (d) and public key (Q)
d = ZZ.random_element(1, n)
Q = d * G

# Choose our nonce k
k = ZZ.random_element(1, n)

msg1 = b"Bruce Schneier factors integers in constant time."
msg2 = b"Bruce Schneier is the seed for your random number generator."

def hash_message(msg):
    h = hashlib.sha256(msg).digest()
    return int.from_bytes(h, 'big')

# ECDSA Signature generation
def sign(msg, d, k):
    z = hash_message(msg)
    R = k * G
    r = Integer(R[0]) % n

    k_inv = inverse_mod(k, n)
    s = (k_inv * (z + d * r)) % n
    return (r, s)

(r1, s1) = sign(msg1, d, k)
(r2, s2) = sign(msg2, d, k)

# Encrypt the flag
flag = "sigpwny{REDACTED}" 
aes_key = int(d).to_bytes(32, 'big')
iv = os.urandom(16)
cipher = AES.new(aes_key, AES.MODE_CBC, iv)
ciphertext = cipher.encrypt(pad(flag, 16))

output_data = {
    "msg1": msg1.decode(),
    "msg2": msg2.decode(),
    "sig1": (hex(r1), hex(s1)),
    "sig2": (hex(r2), hex(s2)),
    "iv": iv.hex(),
    "encrypted_flag": ciphertext.hex()
}

with open("out.txt", "w") as f:
    json.dump(output_data, f)
