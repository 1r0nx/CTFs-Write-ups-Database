#!/usr/bin/env python3
"""
Dormant-Signer (hiCTF, Blockchain) — solve.

Idee : l'Authorizer de production a ete DETRUIT apres avoir "classe" un escrow.
    escrow = final_seal ^ running_digest ^ escrow_mask(liveness_sig)
Le signer a reutilise des nonces ECDSA (meme r) sur ses signatures authorize
=> recuperation de la cle privee => on reproduit sa signature de liveness
(RFC6979 deterministe, low-s) => on calcule le masque => on XOR.

Entree : chain/transactions.jsonl, chain/<deploys>. Hors-ligne, pas d'anvil.
Prereqs: pip install eth-keys rlp pycryptodome
"""
import json, rlp, sys, os
from Crypto.Hash import keccak
from eth_keys import keys
from eth_keys.datatypes import Signature

N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
CHAIN = 7411
def kec(b): h = keccak.new(digest_bits=256); h.update(b); return h.digest()
def caddr(sender, nonce): return kec(rlp.encode([sender, nonce]))[12:]

CHAINDIR = sys.argv[1] if len(sys.argv) > 1 else "chain"

# --- 1. decoder toutes les tx legacy (EIP-155), recuperer l'expediteur ---
rows = []
for line in open(os.path.join(CHAINDIR, "transactions.jsonl")):
    line = line.strip()
    if not line: continue
    t = json.loads(line)
    nonce, gp, gas, to, value, data, v, r, s = rlp.decode(bytes.fromhex(t["raw"][2:]))
    bi = lambda x: int.from_bytes(x, "big") if x else 0
    sh = kec(rlp.encode([nonce, gp, gas, to, value, data, CHAIN, 0, 0]))
    sender = Signature(vrs=(bi(v) - (2*CHAIN+35), bi(r), bi(s))).recover_public_key_from_msg_hash(sh).to_canonical_address()
    rows.append(dict(n=t["n"], nonce=bi(nonce), to=(to.hex() if to else None),
                     value=bi(value), data=data, sender=sender))

# --- 2. adresses des contrats deployes ---
auth = []  # (addr, deploy_tx_n)
for d in rows:
    if d["to"] is None:
        a = caddr(d["sender"], d["nonce"]).hex()
        auth.append((a, d["n"]))

SEL_AUTH = "3dff6cbc"; SEL_SEAL = "b07eeda8"; SEL_DESTROY = "6e0bd282"

def ctor_args(n):
    d = [x for x in rows if x["n"] == n][0]["data"]
    for nrel in (3, 2, 1):
        W = [d[-(7+nrel)*32:][i*32:(i+1)*32] for i in range(7+nrel)]
        if int.from_bytes(W[1],"big") != 0xc0 or int.from_bytes(W[6],"big") != nrel or W[0][:12] != b"\0"*12:
            continue
        return dict(signer=W[0][12:].hex(),
                    relayers=[r[12:].hex() for r in W[7:7+nrel]],
                    quota=[int.from_bytes(W[i],"big") for i in (2,3,4)])

# --- 3. collecter les signatures du signer (dans le calldata authorize) ---
def collect(contract):
    out = []
    for d in rows:
        if d["to"] != contract or d["data"][:4].hex() != SEL_AUTH: continue
        w = lambda i: d["data"][4+i*32:4+(i+1)*32]
        rid, amount, recip = w(0), w(1), w(2)
        v = int.from_bytes(w(3),"big"); r = int.from_bytes(w(4),"big"); s = int.from_bytes(w(5),"big")
        digest = kec(bytes.fromhex(contract).rjust(32,b"\0") + rid + amount + recip)
        try: signer = Signature(vrs=(v-27,r,s)).recover_public_key_from_msg_hash(digest).to_canonical_address().hex()
        except Exception: continue
        out.append(dict(n=d["n"], digest=digest, r=r, s=s, v=v, signer=signer,
                        sender=d["sender"].hex(), rid=rid, amount=int.from_bytes(amount,"big"), recip=recip[12:]))
    return out

# --- 4. cle privee via reutilisation de nonce (meme r), validee par l'adresse ---
def recover_priv(sigs, target):
    byr = {}
    for x in sigs: byr.setdefault(x["r"], []).append(x)
    for r, g in byr.items():
        if len(g) < 2: continue
        g1, g2 = g[0], g[1]
        z1 = int.from_bytes(g1["digest"],"big"); z2 = int.from_bytes(g2["digest"],"big")
        for ss2 in (g2["s"], (N-g2["s"])%N):
            for ss1 in (g1["s"], (N-g1["s"])%N):
                den = (ss1-ss2) % N
                if not den: continue
                kk = ((z1-z2)*pow(den,-1,N)) % N
                if not kk: continue
                d = ((ss1*kk - z1)*pow(r,-1,N)) % N
                if 0 < d < N and keys.PrivateKey(d.to_bytes(32,"big")).public_key.to_canonical_address().hex() == target:
                    return d

# --- 5. running_digest exact = chaine keccak sur les authorize REUSSIS ---
def running_digest(contract, c, sigs):
    used=set(); q=list(c["quota"]); rd=b"\0"*32
    for x in sorted(sigs, key=lambda a:a["n"]):
        idx = next((i for i in range(len(c["relayers"])) if c["relayers"][i]==x["sender"]), None)
        if idx is None or q[idx]<=0 or x["rid"] in used or x["signer"]!=c["signer"]: continue
        used.add(x["rid"]); q[idx]-=1; rd = kec(rd + x["digest"])
    return rd

LIVENESS = kec(b"custody-desk/authorizer/liveness/v1")
ESCROW   = kec(b"custody-desk/authorizer/escrow/v1")

for addr, dn in auth:
    sels = set(x["data"][:4].hex() for x in rows if x["to"] == addr)
    if SEL_AUTH not in sels: continue  # pas un Authorizer
    destroyed = SEL_DESTROY in sels
    c = ctor_args(dn)
    if not c: continue
    sigs = collect(addr)
    d = recover_priv(sigs, c["signer"])
    pk = keys.PrivateKey(d.to_bytes(32,"big"))
    sig = pk.sign_msg_hash(LIVENESS)                       # RFC6979, low-s
    v = sig.v + 27
    mask = kec(ESCROW + sig.r.to_bytes(32,"big") + sig.s.to_bytes(32,"big") + bytes([v]))
    rd = running_digest(addr, c, sigs)
    fn = SEL_DESTROY if destroyed else SEL_SEAL
    final_seal = [x for x in rows if x["to"]==addr and x["data"][:4].hex()==fn][0]["data"][4:36]
    escrow = bytes(a^b^cc for a,b,cc in zip(final_seal, mask, rd))
    tag = "DETRUIT (production)" if destroyed else "scelle (leurre)"
    print(f"Authorizer 0x{addr}  [{tag}]  escrow = {escrow.rstrip(chr(0).encode()).decode(errors='replace')!r}")
    if destroyed:
        print(f"  => FLAG : hiCTF{{{escrow.rstrip(chr(0).encode()).decode()}}}")
