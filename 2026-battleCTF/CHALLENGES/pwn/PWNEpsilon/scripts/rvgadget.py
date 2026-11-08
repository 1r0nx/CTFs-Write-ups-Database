#!/usr/bin/env python3
# RISC-V gadget finder (capstone) for the static vault binary.
import sys, capstone
from elftools.elf.elffile import ELFFile

path = sys.argv[1]
want = sys.argv[2] if len(sys.argv) > 2 else None

elf = ELFFile(open(path,'rb'))
md = capstone.Cs(capstone.CS_ARCH_RISCV, capstone.CS_MODE_RISCV64 | capstone.CS_MODE_RISCVC)
md.detail = False

# gather executable sections
segs = []
for s in elf.iter_sections():
    if s['sh_flags'] & 0x4 and s['sh_type']=='SHT_PROGBITS':  # EXECINSTR
        segs.append((s['sh_addr'], s.data()))

# Terminators: ret (c.jr ra / jalr x0,0(ra)), jalr aX, c.jalr
# We'll scan for terminators then walk back a few instrs.
insns = []  # (addr, size, mnemonic, op_str)
for base, data in segs:
    for ins in md.disasm(data, base):
        insns.append((ins.address, ins.size, ins.mnemonic, ins.op_str))

by_addr = {a:(a,sz,m,o) for (a,sz,m,o) in insns}
addrs = sorted(by_addr)

def is_term(m,o):
    if m in ('ret','c.ret'): return True
    if m in ('jalr','c.jalr','c.jr'):
        return True
    if m=='ecall': return True
    return False

# build gadgets: for each terminator, collect up to N preceding contiguous instrs
N=6
out=[]
idx={a:i for i,a in enumerate(addrs)}
for i,a in enumerate(addrs):
    _,sz,m,o = by_addr[a]
    if not is_term(m,o): continue
    # walk back
    seq=[(a,m,o)]
    cur=a
    for _ in range(N):
        j=idx[cur]
        if j==0: break
        prev=addrs[j-1]
        pa,psz,pm,po=by_addr[prev]
        if pa+psz!=cur: break
        # stop crossing another terminator
        if is_term(pm,po):
            seq.insert(0,(pa,pm,po)); break
        seq.insert(0,(pa,pm,po))
        cur=prev
    # emit gadget string starting at each position
    for st in range(len(seq)):
        g=seq[st:]
        txt=' ; '.join(f'{mm} {oo}'.strip() for (_,mm,oo) in g)
        out.append((g[0][0], txt))

seen=set()
res=[]
for addr,txt in out:
    if txt in seen: continue
    seen.add(txt)
    res.append((addr,txt))

if want:
    for addr,txt in res:
        if want in txt:
            print(f'0x{addr:08x} : {txt}')
else:
    print(f'total gadgets: {len(res)}')
