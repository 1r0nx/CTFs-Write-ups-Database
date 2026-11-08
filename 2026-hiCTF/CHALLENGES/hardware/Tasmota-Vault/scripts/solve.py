#!/usr/bin/env python3
# Tasmota-Vault — unseal reconstruit depuis vault.bec. Déchiffre sealed.bin en AES-256-GCM.
# Prérequis : fichiers LittleFS extraits dans extract_lfs/ (device.id, keyring.bin, sealed.bin).
import hashlib, hmac, struct, os
from Crypto.Cipher import AES

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "extract_lfs")     # device.id, keyring.bin, sealed.bin
device  = open(os.path.join(D, "device.id"),  "rb").read()   # 16 o
keyring = open(os.path.join(D, "keyring.bin"), "rb").read()   # n*(4+32)
sealed  = open(os.path.join(D, "sealed.bin"),  "rb").read()   # IV(12)+ct+tag(16)

ring = {struct.unpack_from('<I', keyring, o)[0]: keyring[o+4:o+36]
        for o in range(0, len(keyring), 36)}

iv, ct, tag = sealed[:12], sealed[12:-16], sealed[-16:]
DOMAIN = b"tasmota-vault/unwrap/v2\x00"

# rotations observées dans mqtt.pcap (topic farm/gw-01/cmnd/VaultRotate)
rotations = {
    7: "9bb1ebe2f5663269d3be1348ee57dc7dbce22b373243aebd67897581cf6f65f0",
    8: "1a3dfb1382455e073f25450c8c8cee24ba89b0a924f86b7103a732ab902a2606",
}
for epoch, noncehex in rotations.items():
    if epoch not in ring:
        continue
    nonce = bytes.fromhex(noncehex)
    msg = DOMAIN + device + struct.pack('<I', epoch) + nonce
    key = hmac.new(ring[epoch], msg, hashlib.sha256).digest()  # clé AES-256
    try:
        pt = AES.new(key, AES.MODE_GCM, nonce=iv).decrypt_and_verify(ct, tag)
        print(f"[epoch {epoch}] TAG OK -> {pt.decode()}")
    except ValueError:
        print(f"[epoch {epoch}] tag FAIL (leurre)")
