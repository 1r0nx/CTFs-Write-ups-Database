# Cipher — hiCTF (script de solve)
import sys,hmac,hashlib
from Crypto.Cipher import AES
from lib import vault
root=bytes.fromhex(sys.argv[1]);salt,recs=vault()
def hkdf(root,salt,info):
    prk=hmac.new(salt,root,hashlib.sha256).digest()
    return hmac.new(prk,info+b'\x01',hashlib.sha256).digest()
for idx,nonce,ct in recs:
    sub=hkdf(root,salt,b'v1'+bytes([idx]))
    c=AES.new(sub,AES.MODE_GCM,nonce=nonce)
    c.update(b'V1LT'+bytes([idx]))
    pt=c.decrypt_and_verify(ct[:-16],ct[-16:])
    t,s=pt.split(b'\x1f',1)
    line=t.decode()+' | '+s.decode()
    print('%02d'%idx,line)
    if 'hiCTF{' in line: print('>>> FLAG',line)
