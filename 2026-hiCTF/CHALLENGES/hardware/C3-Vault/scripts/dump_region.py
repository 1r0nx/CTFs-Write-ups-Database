# C3-Vault — hiCTF (script de solve)
import pickle, sys
from capstone import *
d=open('app_dec.bin','rb').read()
segs=pickle.load(open('segs.pkl','rb'))
la,fo,ln=segs[3]; code=d[fo:fo+ln]
# table d'adresses de chaînes connues pour annoter
STR={}
d0la,d0fo,d0ln=segs[0]
import re
# construit un dico adresse->chaîne pour le rodata (segments 0 et 1)
def strings_map(seg):
    sla,sfo,sln=seg; out={}
    i=sfo; blob=d[sfo:sfo+sln]
    for m in re.finditer(rb'[\x20-\x7e]{3,}', blob):
        out[sla+m.start()]=m.group().decode()
    return out
SMAP={}
for s in (segs[0],segs[1]): SMAP.update(strings_map(s))
md=Cs(CS_ARCH_RISCV, CS_MODE_RISCV32|CS_MODE_RISCVC); md.detail=False
start=int(sys.argv[1],0); end=int(sys.argv[2],0)
sub=code[start-la:end-la]
regval={}
for ins in md.disasm(sub,start):
    m=ins.mnemonic;o=ins.op_str;parts=[p.strip() for p in o.split(',')]
    ann=''
    if m in('lui','c.lui'):
        try: regval[parts[0]]=int(parts[1],0)<<12
        except: pass
    elif m=='auipc':
        try: regval[parts[0]]=ins.address+(int(parts[1],0)<<12)
        except: pass
    elif m in('addi','c.addi') and len(parts)==3:
        b=regval.get(parts[1])
        try: imm=int(parts[2],0)
        except: imm=None
        v=(b+imm) if(b is not None and imm is not None) else None
        regval[parts[0]]=v
        if v in SMAP: ann=f'  ; "{SMAP[v]}"  ({v:#x})'
        elif v is not None: ann=f'  ; {v:#x}'
    elif m in('mv','c.mv'): regval[parts[0]]=regval.get(parts[1])
    elif parts and parts[0] in regval: regval[parts[0]]=None
    if m in('jal','c.jal','jalr','call'):
        ann+='  <CALL>'
    print(f'{ins.address:#010x}: {m:10} {o}{ann}')
