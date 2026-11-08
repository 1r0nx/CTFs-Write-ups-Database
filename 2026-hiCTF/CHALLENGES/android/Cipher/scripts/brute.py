# Cipher — hiCTF (script de solve)
import hashlib,hmac,multiprocessing as mp
from lib import lexicon,anchor,vault,passphrase
W=lexicon();EXP=anchor();SALT,_=vault()
VC=bytes([99,105,112,104,101,114,45,118,101,114,105,102,105,101,114,45,118,51])
BASE=764149760;SPAN=1<<18
def work(rng):
    lo,hi=rng
    for seed in range(lo,hi):
        pw=passphrase(W,seed)
        root=hashlib.pbkdf2_hmac('sha256',pw.encode(),SALT,32768,32)
        if hmac.new(root,VC,hashlib.sha256).digest()[:16]==EXP:
            return (seed,pw,root.hex())
    return None
if __name__=='__main__':
    n=12;chunk=SPAN//n
    ranges=[(BASE+i*chunk,BASE+(i+1)*chunk if i<n-1 else BASE+SPAN) for i in range(n)]
    with mp.Pool(n) as p:
        for r in p.imap_unordered(work,ranges):
            if r: print('FOUND',r);p.terminate();break
        else: print('not found')
