# The-Quiet-Divide — hiCTF (script de solve)
import json,hashlib,hmac,sqlite3,os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
OBJ="/tmp/claude-0/-workspace/4f82a184-2b70-44f2-a1a7-848979c256e1/scratchpad/tqd/objs"
SCR="/tmp/claude-0/-workspace/0d9ec413-ed3a-454d-9f5e-b53392f82479/scratchpad"
def canonical(o):return json.dumps(o,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode()
def digest(r):return hashlib.sha256(r).digest()
def hkdf(raw,sh,ctx):return HKDF(algorithm=hashes.SHA256(),length=32,salt=bytes.fromhex(sh),info=ctx).derive(raw)
MAGIC=b'AVLT10\x00';MASK=(1<<32)-1
def decode_pls2(raw):
    def rr(x,n):return((x>>n)|(x<<(32-n)))&MASK
    seq=rr(int.from_bytes(raw[8:12],'big'),7)^0xC0FFEE21
    queue=int.from_bytes(raw[20:22],'big')^((seq*73)&0xffff)
    load=int.from_bytes(raw[22:24],'big')^((seq*173+queue*7)&0xffff)
    epoch=((int.from_bytes(raw[12:20],'big')-((seq<<13)&((1<<64)-1)))&((1<<64)-1))^0xA96D4E0B7C2296F1
    return {'sequence':seq,'scheduler_queue':queue,'load':load,'epoch_ms':epoch}
firmware=open(SCR+"/firmware_0835.bin","rb").read()
a=bytes.fromhex("74fdca8b1a761cb3bd32c52fde283c549b85d98ed3d776726cf2b48d285ca1cbc43b94c273d7183713e850626497ee8bb73993932fd3247660117232e8091b0e")
q=bytes.fromhex("798fa204c169eacd60b60cc7c2547e99e62b767607301e2f57a0175363efa5d0b511783f7f061d7af8d49b5cf2d7ce49ae21bf6b34f8c75d0e7df582ebb8a602")
frame=bytes.fromhex("504c5332020e217b304cffe0a96d4fbed8d6fe172e5901e05a3ac5c3583af37d")
codec=digest(b'MB10/CODEC/STATE\x00'+canonical(decode_pls2(frame))+frame)
ARCH_SALT="6d562eb7d1e5ef0b993548337b8a2b9b"
TERM="b34dc728c1fa1525020b1969a8af2698b2bcd91a95d58b3e3b940de35deda6e1"
aad=canonical({'schema':'mb-corpus/10','commit':TERM})
events=json.load(open(OBJ+"/audit(1)"))["events"]
chain=digest(canonical(events))
fw=hmac.new(chain,b'MB10/FULL/ELF\x00'+firmware,hashlib.sha256).digest()
evidence=chain+fw+a+q+codec
key=hkdf(evidence,ARCH_SALT,b'MIRRORBREAK/10/RECORD-VAULT')
print("codec=",codec.hex())
arch=["affbe6e628390923b0e3c645113c37ab","22eaa76cd29c9977062596cfc39ac887","5a2c8adef3c0846a2d0fb62d00844c64"]
for i,name in enumerate(arch):
    blob=open(OBJ+"/"+name,"rb").read()
    pt=AESGCM(key).decrypt(blob[7:19],blob[19:],aad)
    p=f"{SCR}/corpus_{i}.sqlite"; open(p,"wb").write(pt)
    con=sqlite3.connect(p);cur=con.cursor()
    tbls=[r[0] for r in cur.execute("select name from sqlite_master where type='table'")]
    print(f"\n=== archive {name} -> {p}  tables={tbls}")
    for t in tbls:
        cols=[c[1] for c in cur.execute(f"PRAGMA table_info({t})")]
        n=cur.execute(f"select count(*) from {t}").fetchone()[0]
        print(f"  {t} ({n} lignes) cols={cols}")
        for row in cur.execute(f"select * from {t} limit 4"):
            print("    ", [ (x[:40]+'..' if isinstance(x,str) and len(x)>42 else (f'<{len(x)}B>' if isinstance(x,(bytes,bytearray)) else x)) for x in row])
    con.close()
# sauvegarde evidence/codec pour l'etape finale
open(SCR+"/evidence.bin","wb").write(evidence)
print("\nevidence sauvegardee", len(evidence),"o")
