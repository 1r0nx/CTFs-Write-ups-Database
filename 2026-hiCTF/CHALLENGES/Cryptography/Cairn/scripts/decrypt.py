# Déchiffre le flag à partir de j_T (sortie de ./cairn : "a_hex b_hex")
# Usage : python -I decrypt.py <challenge.json> <jT.txt>
import sys, json, hashlib, base64
from Crypto.Cipher import AES

d = json.load(open(sys.argv[1]))
a, b = (int(x, 16) for x in open(sys.argv[2]).read().split())
ser = a.to_bytes(32, "little") + b.to_bytes(32, "little")   # ser(j_T)
key = hashlib.sha256(ser + b"IsogenyLabyrinth").digest()
c = AES.new(key, AES.MODE_GCM, nonce=base64.b64decode(d["nonce_b64"]))
# decrypt_and_verify lève une erreur si le tag GCM ne correspond pas -> preuve que j_T est juste
print(c.decrypt_and_verify(base64.b64decode(d["ciphertext_b64"]), base64.b64decode(d["tag_b64"])).decode())
