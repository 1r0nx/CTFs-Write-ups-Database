# Tasmota-Vault — hiCTF (script de solve)
import struct, sys
OPS="ADD SUB MUL DIV MOD LT LE EQ NE GT GE AND OR XOR SHL SHR CONNECT NEG FLIP LDNIL LDBOOL LDINT LDCONST MOVE GETGBL SETGBL GETUPV SETUPV JMP JMPT JMPF CALL RET CLOSURE GETMBR GETMET SETMBR GETIDX SETIDX SETSUPER CLOSE IMPORT EXBLK CATCH RAISE CLASS GETNGBL SETNGBL".split()
BE_NIL,BE_INT,BE_REAL,BE_BOOL,BE_STRING,BE_CLASS=0,1,2,3,16,17
data=open(sys.argv[1],'rb').read()
pos=8
def u8():
    global pos; v=data[pos]; pos+=1; return v
def u16():
    global pos; v=struct.unpack_from('<H',data,pos)[0]; pos+=2; return v
def u32():
    global pos; v=struct.unpack_from('<I',data,pos)[0]; pos+=4; return v
def s32():
    global pos; v=struct.unpack_from('<i',data,pos)[0]; pos+=4; return v
def rdstr():
    global pos; n=u16(); s=data[pos:pos+n]; pos+=n; return s.decode('latin1')
sizeinfo=data[4]; USE64=sizeinfo&1; REAL64=(sizeinfo>>1)&1
builtin=u32(); gcount=u32()
gbls=[rdstr() for _ in range(gcount)]
IsBxMax=((1<<18)-1)>>1
def read_value():
    t=u8()
    if t==BE_INT:
        return ('int', (u32()|(u32()<<32)) if USE64 else s32())
    if t==BE_REAL:
        if REAL64: return ('real', struct.unpack('<d',data[pos-0:pos+8])[0]) 
        return ('real', struct.unpack('<f', struct.pack('<I',u32()))[0])
    if t==BE_STRING: return ('str', rdstr())
    if t==BE_NIL: return ('nil',None)
    if t==BE_BOOL: return ('bool', u8())
    if t==BE_CLASS: return ('class', read_class())
    return ('T%d'%t,None)
def read_class():
    name=rdstr(); nvar=u32(); nmeth=u32()
    # skip members: this is complex; for our agent likely few classes. Best-effort.
    res={'name':name,'nvar':nvar,'nmeth':nmeth,'methods':[]}
    total=nmeth+nvar
    # members: for each (nmeth methods then nvar var names)? Save writes interleaved via map order.
    # Simplify: read nmeth entries (name+proto) then nvar var names
    for _ in range(nmeth):
        mname=rdstr()
        if mname=='' : continue
        res['methods'].append(mname)
        read_proto()  # proto follows
    for _ in range(nvar):
        rdstr()
    return res
def rkstr(v, consts):
    # 9-bit field; bit8 => const
    if v & 0x100:
        idx=v&0xFF
        if idx<len(consts):
            k=consts[idx]
            return f"K{idx}({fmtk(k)})"
        return f"K{idx}"
    return f"R{v}"
def fmtk(k):
    t,val=k
    if t=='str': return repr(val)
    return f"{t}:{val}"
protos=[]
def read_proto(depth=0):
    name=rdstr(); source=rdstr()
    argc=u8(); nstack=u8(); varg=u8(); u8()
    codesize=u32()
    code=[u32() for _ in range(codesize)]
    nconst=u32()
    consts=[read_value() for _ in range(nconst)]
    nproto=u32()
    subs=[read_proto(depth+1) for _ in range(nproto)]
    nupv=u8()
    upvals=[(u8(),u8()) for _ in range(nupv)]
    p={'name':name,'source':source,'argc':argc,'nstack':nstack,'varg':varg,
       'code':code,'consts':consts,'subs':subs,'upvals':upvals}
    return p
def disp(p,prefix=''):
    print(f"\n=== PROTO {prefix}{p['name']!r} argc={p['argc']} nstack={p['nstack']} varg={p['varg']} nconst={len(p['consts'])} nsub={len(p['subs'])} nupv={len(p['upvals'])} ===")
    for i,k in enumerate(p['consts']): print(f"   K{i}= {fmtk(k)}")
    for i,uv in enumerate(p['upvals']): print(f"   U{i}= instack={uv[0]} idx={uv[1]}")
    C=p['consts']
    for pc,ins in enumerate(p['code']):
        op=(ins>>26)&0x3F; ra=(ins>>18)&0xFF; rkb=(ins>>9)&0x1FF; rkc=ins&0x1FF
        bx=ins&0x3FFFF; sbx=bx-IsBxMax
        nm=OPS[op] if op<len(OPS) else f"OP{op}"
        s=f"  {pc:3d}: {nm:9s}"
        if nm in ('LDCONST',): s+=f" R{ra}, K{bx}({fmtk(C[bx]) if bx<len(C) else '?'})"
        elif nm in ('GETGBL','SETGBL','GETUPV','SETUPV','CLOSURE'): s+=f" R{ra}, {bx}"
        elif nm in ('LDINT',): s+=f" R{ra}, {sbx}"
        elif nm in ('JMP',): s+=f" -> {pc+1+sbx}"
        elif nm in ('JMPT','JMPF'): s+=f" R{ra} -> {pc+1+sbx}"
        elif nm in ('CLASS',): s+=f" K{bx}({fmtk(C[bx]) if bx<len(C) else '?'})"
        elif nm in ('CALL',): s+=f" R{ra}, nargs={rkb}"
        elif nm in ('RET',): s+=f" R{ra}, {rkstr(rkb,C) if rkb else ''}"
        elif nm in ('GETNGBL','SETNGBL'): s+=f" R{ra}, {rkstr(rkb,C)}"
        elif nm in ('GETMBR','GETMET','SETMBR','GETIDX','SETIDX','IMPORT','ADD','SUB','MUL','DIV','MOD','LT','LE','EQ','NE','GT','GE','AND','OR','XOR','SHL','SHR','CONNECT','MOVE'):
            s+=f" R{ra}, {rkstr(rkb,C)}, {rkstr(rkc,C)}"
        elif nm in ('LDNIL','CLOSE'): s+=f" R{ra}"
        elif nm in ('LDBOOL',): s+=f" R{ra}, {rkb}, {rkc}"
        else: s+=f" ra={ra} b={rkb} c={rkc} bx={bx} sbx={sbx}"
        print(s)
    for i,sp in enumerate(p['subs']):
        disp(sp,prefix=f"{prefix}{p['name']}.")
top=read_proto()
print(f"builtin_count={builtin} gcount={gcount} sizeinfo={sizeinfo} bytes_consumed={pos}/{len(data)}")
disp(top)
