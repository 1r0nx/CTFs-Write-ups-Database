# C3-Vault — hiCTF (script de solve)
import pickle, sys
from capstone import *
d=open('app_dec.bin','rb').read()
segs=pickle.load(open('segs.pkl','rb'))
# seg3 = code IROM
la,fo,ln = segs[3]
code=d[fo:fo+ln]
md=Cs(CS_ARCH_RISCV, CS_MODE_RISCV32|CS_MODE_RISCVC)
md.detail=False
insns=list(md.disasm(code, la))
# reconstruire les constantes d'adresse (lui/auipc + addi) par registre
def scan_for_addr(target):
    regval={}
    hits=[]
    for ins in insns:
        m=ins.mnemonic; o=ins.op_str
        parts=[p.strip() for p in o.split(',')]
        if m in ('lui','c.lui') and len(parts)==2:
            try: regval[parts[0]]=int(parts[1],0)<<12
            except: regval[parts[0]]=None
        elif m=='auipc' and len(parts)==2:
            try: regval[parts[0]]=ins.address + (int(parts[1],0)<<12)
            except: pass
        elif m in ('addi','c.addi','mv','c.mv','addiw') and len(parts)>=2:
            if m in ('mv','c.mv'):
                regval[parts[0]]=regval.get(parts[1])
            elif len(parts)==3:
                base=regval.get(parts[1])
                try: imm=int(parts[2],0)
                except: imm=None
                regval[parts[0]]= (base+imm) if (base is not None and imm is not None) else None
            if regval.get(parts[0])==target:
                hits.append(ins.address)
        else:
            # invalide les registres écrits (approx : premier opérande)
            if parts and parts[0] in regval and m not in ('sw','sh','sb','beq','bne','blt','bge','bltu','bgeu','c.beqz','c.bnez'):
                regval[parts[0]]=None
    return hits
for t in [int(x,0) for x in sys.argv[1:]]:
    print(f'target {t:#x} référencé vers:', [hex(a) for a in scan_for_addr(t)])
