# The-Quiet-Divide — hiCTF (script de solve)
import json,hashlib,hmac,sqlite3,struct,base64,itertools
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
SCR="/tmp/claude-0/-workspace/0d9ec413-ed3a-454d-9f5e-b53392f82479/scratchpad"
def hex_digest(r):return hashlib.sha256(r).hexdigest()
def canonical(o):return json.dumps(o,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False).encode()
def hkdf(raw,sh,ctx):return HKDF(algorithm=hashes.SHA256(),length=32,salt=bytes.fromhex(sh),info=ctx).derive(raw)
codec=bytes.fromhex("c358a8d65550291f281fb21927a04e3462d0d33e0063eb6594b21a79181007c9")
evidence=open(SCR+"/evidence.bin","rb").read()
TERM="b34dc728c1fa1525020b1969a8af2698b2bcd91a95d58b3e3b940de35deda6e1"
WITNESS="1d8cf57f013e2e45f9231a6ef2f6fad2412a3c4c9bda973a30667c849c57c8ba4280cb2850f63c4d54c599a051c9cee8ac40bade16255db54235e1ae00cd9e0a"
SEAL_SALT="ded3d12c395ca229af8ed23e9268ab99"
body=json.load(open("/workspace/hiCTF/Forensics/The-Quiet-Divide/work/audit_seal.json"))["seal"]["body"]
cipher=base64.b64decode(body["ciphertext_b64"]); nonce=bytes.fromhex(body["nonce_hex"])
fields=('schema','terminal_event_sha256','attestation_sha256','observation_sha256','firmware_sha256','archive_batch_sha256','checkpoint_sha256')
seal_aad=canonical({k:body[k] for k in fields})
def unmask(tx_id,ordinal,encoded):
    pad=hmac.new(codec,b'MB10/FRAGMENT\x00'+tx_id.encode()+struct.pack('>I',ordinal),hashlib.sha256).digest()
    return bytes(x^y for x,y in zip(encoded,pad))
def tmc(material,tx_id):
    return hex_digest(material+bytes.fromhex(TERM)+bytes.fromhex(tx_id)+codec)
def try_seal(key,tag):
    try:
        pt=AESGCM(key).decrypt(nonce,cipher,seal_aad)
        print("### FLAG ###",tag,pt); return True
    except Exception: return False
mats={}  # tx_id -> (material, origin, case_commit, relckpt, frag_commit)
for i in range(3):
    con=sqlite3.connect(f"{SCR}/corpus_{i}.sqlite");cur=con.cursor()
    trans={r[0]:r for r in cur.execute("select tx_id,case_commit,device_nonce,counter,origin,version,release_checkpoint from transfers")}
    rec={r[0]:r[3] for r in cur.execute("select tx_id,observed_state,disposition,fragment_commit from receipts")}
    frg={}
    for tx,o,pay,dg in cur.execute("select tx_id,ord,payload,digest from fragments"):
        frg.setdefault(tx,{})[o]=pay
    for tx,meta in trans.items():
        mat=b"".join(unmask(tx,o,frg[tx][o]) for o in sorted(frg[tx]))
        mats[tx]=(mat,meta[4],meta[1],meta[6],rec.get(tx),i)
    con.close()
# verif commit + liste des tx authoritaires
auth=[]
for tx,(mat,origin,cc,rck,fc,ai) in mats.items():
    ok = (tmc(mat,tx)==fc)
    is_auth = cc==TERM and rck.startswith("5e4f78ad")
    if is_auth: auth.append((ai,tx,mat))
    print(f"arch{ai} tx={tx} origin={origin} commit_ok={ok} auth={is_auth} cc={cc[:8]} rck={rck[:8]}")
print("\nauthoritaires:",[(a,t) for a,t,_ in auth])
# tentatives decrypt_seal
import itertools as it
# 1) material = chaque tx seule
for ai,tx,mat in mats_list if False else []:
    pass
for tx,(mat,origin,cc,rck,fc,ai) in mats.items():
    if try_seal(hkdf(mat+evidence+bytes.fromhex(WITNESS),SEAL_SALT,b'MIRRORBREAK/10/PRODUCTION-CASE'),f"single {tx}"):
        raise SystemExit
# 2) material = concat des 3 tx authoritaires (ordre par archive 0,1,2)
auth_sorted=[m for _,_,m in sorted(auth)]
for perm in it.permutations(range(len(auth_sorted))):
    cat=b"".join(auth_sorted[k] for k in perm)
    if try_seal(hkdf(cat+evidence+bytes.fromhex(WITNESS),SEAL_SALT,b'MIRRORBREAK/10/PRODUCTION-CASE'),f"concat{perm}"):
        raise SystemExit
# 3) material = commit hex digest bytes de la tx authoritaire
for ai,tx,mat in auth:
    cm=bytes.fromhex(tmc(mat,tx))
    if try_seal(hkdf(cm+evidence+bytes.fromhex(WITNESS),SEAL_SALT,b'MIRRORBREAK/10/PRODUCTION-CASE'),f"commitbytes {tx}"):
        raise SystemExit
print("aucune variante simple n'a authentifie")
