# C3-Vault — hiCTF (script de solve)
import struct, sys
d=open('app_dec.bin','rb').read()
magic,segcnt,_,_=d[0],d[1],d[2],d[3]
entry=struct.unpack('<I',d[4:8])[0]
print(f'magic={magic:#x} segments={segcnt} entry={entry:#x}')
off=24
segs=[]
for s in range(segcnt):
    la,ln=struct.unpack('<II',d[off:off+8]); off+=8
    data=d[off:off+ln]; 
    segs.append((la,off,ln))
    print(f'seg{s}: vaddr={la:#010x} fileoff={off:#x} len={ln:#x} ({ln})')
    off+=ln
import pickle
pickle.dump(segs, open('segs.pkl','wb'))
# chercher les chaînes
def find(s):
    for la,fo,ln in segs:
        i=d.find(s, fo, fo+ln)
        if i>=0:
            return la+(i-fo), i
    return None,None
for s in [b'C3VAULT-AUTH-V2', b'c3-vault/device-key/v2', b'C3VAULT/2 READY', b'CHALLENGE', b'enrollment(device_id, key)', b'vault_v2', b'seed']:
    va,fo=find(s)
    print(f'{s!r:40} vaddr={va:#x if va else 0}' if va else f'{s!r:40} introuvable', f'fileoff={fo:#x}' if fo else '')
