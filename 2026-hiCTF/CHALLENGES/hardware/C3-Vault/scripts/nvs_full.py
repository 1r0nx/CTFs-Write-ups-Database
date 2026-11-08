# C3-Vault — hiCTF (script de solve)
import struct
d=open('nvs_plain.bin','rb').read()
TYPES={0x01:'U8',0x11:'I8',0x02:'U16',0x12:'I16',0x04:'U32',0x14:'I32',0x08:'U64',0x18:'I64',
       0x21:'STR',0x41:'BLOB',0x42:'BLOB_DATA',0x48:'BLOB_IDX'}
ns={}
for page in range(0,len(d),4096):
    pg=d[page:page+4096]
    if len(pg)<4096: break
    state=struct.unpack('<I',pg[0:4])[0]
    if state==0xFFFFFFFF: continue
    bm=pg[32:64]
    i=0
    while i<126:
        bs=(bm[i//4]>>((i%4)*2))&3
        e=pg[64+i*32:64+i*32+32]
        nsidx,typ,span,chunk=e[0],e[1],e[2],e[3]
        key=e[8:24].split(b'\x00')[0].decode('latin1')
        if bs==2 and typ in TYPES:
            tn=TYPES[typ]
            if nsidx==0:
                ns[e[24]]=key; print(f'NS idx={e[24]} {key!r}')
            else:
                nsn=ns.get(nsidx,f'ns#{nsidx}')
                if tn in ('STR','BLOB_DATA'):
                    sz=struct.unpack('<H',e[24:26])[0]
                    blob=pg[64+(i+1)*32:64+(i+1)*32+sz]
                    print(f'  [{nsn}] {key!r} {tn} size={sz} chunk={chunk} data={blob.hex()}')
                    try:
                        s=blob.decode('utf-8'); print(f'        str={s!r}')
                    except: pass
                    i+=span-1
                elif tn=='BLOB_IDX':
                    sz=struct.unpack('<I',e[24:28])[0]
                    print(f'  [{nsn}] {key!r} BLOB_IDX total_size={sz}')
                else:
                    v=struct.unpack('<q',e[24:32])[0]
                    print(f'  [{nsn}] {key!r} {tn} = {v} ({v&0xffffffffffffffff:#x})')
        i+=1
