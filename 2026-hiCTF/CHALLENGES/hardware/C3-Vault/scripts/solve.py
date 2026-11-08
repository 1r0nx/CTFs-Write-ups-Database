# C3 Vault : calcule la réponse d'authentification (reconstruite depuis le firmware) et la soumet.
import socket, ssl, hmac, hashlib, re, sys
HOST='c3-vault-ecb2f59e8e34.chall.hiddeninvestigations.net'; PORT=1337
device_id = bytes.fromhex('ee0315f3953aad298d7f3f43973ad618')
seed_v2 = bytes.fromhex('826e4e9e65c0ce89f413b7c291bb7e84185c64d4ec8769805227253b985083c5')
seed_v1 = bytes.fromhex('d857200f87a1728b5220a4d77c31d7d9ee9bf8992ad16dbb398d05844676aa4f')
def H(key,msg): return hmac.new(key,msg,hashlib.sha256).digest()
def device_key(seed, gen):
    return H(seed, b'c3-vault/device-key/v2\x00' + device_id + gen.to_bytes(4,'little'))
def response(dk, challenge):
    return H(dk, b'C3VAULT-AUTH-V2\x00' + challenge + device_id)
def connect():
    ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
    s=ctx.wrap_socket(socket.create_connection((HOST,PORT),timeout=20),server_hostname=HOST); s.settimeout(10); buf=b''
    try:
        while b'CHALLENGE' not in buf or b'Commands' not in buf:
            d=s.recv(4096)
            if not d: break
            buf+=d
    except socket.timeout: pass
    return s,buf.decode(errors='replace')
def drain(s):
    s.settimeout(6); out=b''
    try:
        while True:
            d=s.recv(4096)
            if not d: break
            out+=d
    except socket.timeout: pass
    return out.decode(errors='replace')

seed = seed_v2; gen = 7
if len(sys.argv)>1: gen=int(sys.argv[1])
if len(sys.argv)>2 and sys.argv[2]=='v1': seed=seed_v1
s,greet=connect()
print(greet.strip())
ch=bytes.fromhex(re.search(r'CHALLENGE ([0-9a-f]{64})',greet).group(1))
dk=device_key(seed,gen); resp=response(dk,ch)
print(f'[gen={gen} seed={"v1" if seed==seed_v1 else "v2"}] resp={resp.hex()}')
s.sendall(b'AUTH '+resp.hex().encode()+b'\n')
print(drain(s).strip())
s.close()
