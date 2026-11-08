#!/usr/bin/env python3
# tooooo fancy 😏 — reverse d'un checker Tcl compile (.tbc = TclPro ByteCode).
#
# 1) Decoder le conteneur .tbc : alphabet base85 LITTLE-ENDIAN custom (cf. tbcload/cmpRead.c),
#    grammaire = header(13 ints) + byte-seqs(code, locmaps) + tableau de 45 litteraux.
# 2) Les litteraux donnent le programme : flag lu en char-codes (= x), `wtf` = b (36 valeurs),
#    `wat` = 1296 valeurs rangees dans des variables nommees par une CHAINE DE HASH MD5
#    (position p <-> wat[p-1]), flag length = 36.
# 3) Le check calcule, pour chaque n : epic_n = sum_k coeff[n][k] * input[35-k], et exige
#    epic_n == b[n] (unfanciness |= epic_n ^ b[n] doit valoir 0). coeff = valeur a la position
#    courante de la chaine, avancee de Tn=((n+3)*n+1)//2 (si k==0) puis de offset=n+k+1
#    (ou 71-offset si k>=35-n). Les positions couvrent 1..1296.
#    => systeme lineaire A x = b, 36x36, resolu exactement.  FLAG = sigpwny{1_hope_that_tcls_y0ur_f4ncy}

import sys
from fractions import Fraction as F

# ---- alphabet base85 de TclPro (decodeMap, little-endian) ----
dm=[None]*128
def sv(ch,v): dm[ord(ch)]=v
sv('!',0); sv('#',2); sv('%',4); sv('&',5); sv("'",6); sv('(',7); sv(')',8); sv('*',9)
sv('+',10); sv(',',11); sv('-',12); sv('.',13); sv('/',14)
for k,c in enumerate(range(ord('0'),ord('9')+1)): dm[c]=15+k
sv(':',25); sv(';',26); sv('<',27); sv('=',28); sv('>',29); sv('?',30); sv('@',31)
for k,c in enumerate(range(ord('A'),ord('Z')+1)): dm[c]=32+k
sv('^',61); sv('_',62); sv('`',63)
for k,c in enumerate(range(ord('a'),ord('u')+1)): dm[c]=64+k
sv('v',1); sv('w',3); sv('x',58); sv('y',59); sv('|',60)
ZCH='z'

def parse_tbc(path):
    raw=open(path).read()
    hdr="TclPro ByteCode 2 0 1.7 8.6"
    IMG=raw[raw.index(hdr)+len(hdr):]; pos=[0]; N=len(IMG)
    def skipws():
        while pos[0]<N and IMG[pos[0]] in " \t\r\n": pos[0]+=1
    def rint():
        skipws(); st=pos[0]
        while pos[0]<N and IMG[pos[0]] not in " \t\r\n": pos[0]+=1
        return int(IMG[st:pos[0]])
    def a85(nbytes):
        out=bytearray(); buf=[]; btd=nbytes
        while btd>0:
            c=IMG[pos[0]]; pos[0]+=1
            if c==ZCH:
                assert not buf; out+=b'\x00\x00\x00\x00'; btd-=4; continue
            code=dm[ord(c)]
            if code is None: continue          # whitespace / skip
            buf.append(code)
            if btd>=4:
                if len(buf)==5:
                    w=buf[0]+85*buf[1]+7225*buf[2]+614125*buf[3]+52200625*buf[4]
                    out+=bytes([w&0xff,(w>>8)&0xff,(w>>16)&0xff,(w>>24)&0xff]); buf=[]; btd-=4
            elif len(buf)==btd+1:
                g=buf+[0]*(5-len(buf))
                w=g[0]+85*g[1]+7225*g[2]+614125*g[3]+52200625*g[4]
                for k in range(btd): out.append((w>>(8*k))&0xff)
                btd=0; buf=[]
        return bytes(out)
    def byteseq(exp):
        hl=rint(); assert exp<0 or exp==hl; return a85(hl)
    h=[rint() for _ in range(13)]
    numCode,numLit,cds,cls,sds,sls=h[2],h[3],h[9],h[10],h[11],h[12]
    byteseq(numCode); byteseq(cds); byteseq(cls)
    if sds>=0: byteseq(sds)
    if sls>=0: byteseq(sls)
    assert rint()==numLit
    lits=[]
    for _ in range(numLit):
        skipws(); tc=IMG[pos[0]]; pos[0]+=1
        if tc=='x':
            hl=rint(); lits.append(a85(hl))
        elif tc=='s':
            hl=rint()
            while IMG[pos[0]]!='\n': pos[0]+=1
            pos[0]+=1; lits.append(IMG[pos[0]:pos[0]+hl].encode('latin1')); pos[0]+=hl
        elif tc in 'idb':
            skipws(); st=pos[0]
            while IMG[pos[0]] not in " \t\r\n": pos[0]+=1
            lits.append(('num',IMG[st:pos[0]]))
        else:
            raise ValueError(f"type {tc!r}")
    return lits

def solve_lin(M,vec,L):
    A=[[F(M[i][j]) for j in range(L)]+[F(vec[i])] for i in range(L)]
    for c in range(L):
        piv=next((r for r in range(c,L) if A[r][c]!=0),None)
        if piv is None: return None
        A[c],A[piv]=A[piv],A[c]; pv=A[c][c]; A[c]=[v/pv for v in A[c]]
        for r in range(L):
            if r!=c and A[r][c]!=0:
                f=A[r][c]; A[r]=[a-f*bb for a,bb in zip(A[r],A[c])]
    return [A[i][L] for i in range(L)]

def main():
    lits=parse_tbc("main.tbc")
    b  =[int(x) for x in lits[14].decode().split()]      # wtf  (b, 36)
    wat=[int(x) for x in lits[19].decode().split()]      # wat  (A values, 1296)
    L=36
    coeff=[[0]*L for _ in range(L)]
    for n in range(L):
        p=1
        Tn=((n+3)*n+1)//2
        for k in range(L):
            if k==0: p+=Tn
            coeff[n][k]=wat[p-1]
            off=n+k+1
            if k>=L-n-1: off=2*L-off-1
            p+=off
    M=[[coeff[n][L-1-j] for j in range(L)] for n in range(L)]   # sum_k c[n][k]*x[35-k]=b[n]
    x=solve_lin(M,b,L)
    assert x and all(v.denominator==1 for v in x)
    flag="".join(chr(int(v)) for v in x)
    assert all(sum(coeff[n][k]*int(x[L-1-k]) for k in range(L))==b[n] for n in range(L))
    print(flag)

if __name__=="__main__":
    main()
