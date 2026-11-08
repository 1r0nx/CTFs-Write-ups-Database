#!/usr/bin/env python3
"""Pruned-Ledger (hiCTF) — reconstruit hors-ligne la case file d'une case donnee.
Usage: solve.py <chain_dir> <caseTag hex ex: ca5ef11e>
Prereqs: pip install eth-keys rlp pycryptodome"""
import json, rlp, sys, os
from Crypto.Hash import keccak
from eth_keys.datatypes import Signature
def k(b): h=keccak.new(digest_bits=256); h.update(b); return h.digest()
CHAINDIR=sys.argv[1]; WANT=sys.argv[2].lower().lstrip("0x")
CHAIN=int(json.load(open(os.path.join(CHAINDIR,"genesis.json")))["config"]["chainId"])
SEAL=k(b"hictf.pruned-ledger.seal"); NOTE=k(b"hictf.pruned-ledger.note")
rows=[]
for line in open(os.path.join(CHAINDIR,"transactions.jsonl")):
    line=line.strip()
    if not line: continue
    t=json.loads(line); f=rlp.decode(bytes.fromhex(t["raw"][2:]))
    nonce,gp,gas,to,value,data,v,r,s=f; bi=lambda x:int.from_bytes(x,'big') if x else 0
    sh=k(rlp.encode([nonce,gp,gas,to,value,data,CHAIN,0,0]))
    snd=Signature(vrs=(bi(v)-(2*CHAIN+35),bi(r),bi(s))).recover_public_key_from_msg_hash(sh).to_canonical_address()
    rows.append(dict(n=t["n"],nonce=bi(nonce),to=(to.hex() if to else None),value=bi(value),data=data,sender=snd))
caddr=lambda s,nn:k(rlp.encode([s,nn]))[12:]
creates=[(d["n"],d["sender"].hex(),d["nonce"],caddr(d["sender"],d["nonce"]).hex(),d["data"]) for d in rows if d["to"] is None]
def rd(b):
    s=b.rstrip(b'\0'); return s.decode() if s and all(32<=c<127 for c in s) else None
# relais: last2 words = caseTag(bytes4), nextHop(address)
relay={}
for n,dep,nn,addr,data in creates:
    w1,w2=data[-64:-32],data[-32:]; relay[addr]=(w1[:4].hex(),w2[12:].hex())
# suivre la piste du tag voulu jusqu'a son terminus (Ledger)
hops=[a for a,(tg,nh) in relay.items() if tg==WANT]
nexts={nh for a,(tg,nh) in relay.items() if tg==WANT}
ledger=[nh for nh in nexts if nh not in {a for a,_ in relay.items()}]  # terminus hors relais
# terminus = nextHop qui n'est pas lui-meme un relais du meme tag -> le Ledger
tagged=set(hops)
terminal=[nh for a,(tg,nh) in relay.items() if tg==WANT and nh not in tagged]
L=terminal[0]
print("case 0x%s -> Ledger 0x%s"%(WANT,L))
dn=[n for n,_,_,addr,_ in creates if addr==L][0]
cdata=[d for d in creates if d[3]==L][0][4]
cr,mn,uh=cdata[-96:][0:32],cdata[-96:][32:64],cdata[-96:][64:96]
op=[d["sender"].hex() for d in rows if d["n"]==dn][0]
seq=sorted([x for x in rows if x["to"]==L and len(x["data"])>=4],key=lambda a:a["n"])
rec=None; rec_seal=None
for c in seq:
    s4=c["data"][:4].hex()
    if s4==k(b"configure(bytes32)")[:4].hex() and c["sender"].hex()==op: rec=c["data"][4:36]
    elif s4==k(b"seal(bytes32)")[:4].hex() and c["sender"].hex()==op:
        rec_seal=rec; sm=c["data"][4:36]
laddr=bytes.fromhex(L)
entry=bytes(a^b for a,b in zip(sm,k(SEAL+laddr+rec_seal)))
cands={d["sender"].hex() for d in rows}|{d["to"] for d in rows if d["to"]}
note=None
for caller in cands:
    nb=bytes(a^b for a,b in zip(mn,k(NOTE+laddr+bytes.fromhex(caller))))
    if rd(nb): note=rd(nb); break
fields=[rd(cr),rd(rec_seal),rd(entry),note]
print("case file:", fields)
print("phrase  :", " ".join(fields))
print("FLAG    : hiCTF{%s}"%"_".join(fields))
