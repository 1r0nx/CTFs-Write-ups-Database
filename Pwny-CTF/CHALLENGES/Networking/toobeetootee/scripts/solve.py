#!/usr/bin/env python3
"""
toobeetootee (2b2t) — reconstruire le flag griefé dans un monde Minetest à partir du pcap.

Idée : popbob a CASSÉ des blocs du flag (REMOVENODE). Le monde final (world.zip) est abîmé,
mais la capture réseau contient l'état d'origine (BLOCKDATA) + les suppressions.
On reconstruit le flag = (nodes du flag vus dans les BLOCKDATA) ∪ (positions REMOVENODE, qui
étaient du flag), on garde la façade (plan X=-357) et on projette sur le plan Y-Z.

Nécessite seulement tshark + Python (zlib). Génère work/flag_solved.png.
Flag : uiuctf{BudG3t_c4ves_N_cl1fFs}  ("Budget Caves N Cliffs" -> clin d'œil à Minecraft "Caves & Cliffs")
"""
import subprocess, struct, zlib
PCAP="toobeetootee.pcap"; SERVER="192.168.1.201"; FLAG_NODE=54; FACE_X=-357

def u16(b,o): return struct.unpack('>H', b[o:o+2])[0]
def s16(b,o): return struct.unpack('>h', b[o:o+2])[0]

# 1) Récupérer les payloads serveur->client dans l'ordre
raw = subprocess.check_output(
    ["tshark","-r",PCAP,"-Y",f"ip.src=={SERVER} && udp.srcport==30000 && data",
     "-T","fields","-e","data.data"], text=True, stderr=subprocess.DEVNULL)

splits={}; blocks={}; removed=[]
def decode_block(ser):
    # trouve le flux zlib qui donne >=16384 octets (4096 nodes * (2+1+1))
    for off in range(2,9):
        if off<len(ser) and ser[off]==0x78:
            try:
                r=zlib.decompressobj().decompress(ser[off:])
                if len(r)>=16384: return struct.unpack('>4096H', r[:8192])  # param0
            except Exception: pass
    return None
def handle(cmd_payload):
    if len(cmd_payload)<2: return
    cmd=u16(cmd_payload,0)
    if cmd==0x22 and len(cmd_payload)>=8:                 # REMOVENODE
        removed.append((s16(cmd_payload,2),s16(cmd_payload,4),s16(cmd_payload,6)))
    elif cmd==0x20 and len(cmd_payload)>=9:               # BLOCKDATA
        X,Y,Z=s16(cmd_payload,2),s16(cmd_payload,4),s16(cmd_payload,6)
        if (X,Y,Z) in blocks: return                      # 1er état vu = avant grief
        p0=decode_block(cmd_payload[8:])
        if p0: blocks[(X,Y,Z)]=p0
def parse(data, ch):                                      # déballe RELIABLE / réassemble SPLIT
    if not data: return
    t=data[0]
    if t==0x01: handle(data[1:])                          # ORIGINAL
    elif t==0x02:                                         # SPLIT
        seq=u16(data,1); cnt=u16(data,3); num=u16(data,5)
        d=splits.setdefault((ch,seq),{}); d[num]=data[7:]; d['n']=cnt
        if len([k for k in d if isinstance(k,int)])==cnt:
            handle(b''.join(d[i] for i in range(cnt))); splits.pop((ch,seq),None)
    elif t==0x03: parse(data[3:], ch)                     # RELIABLE -> paquet interne

for line in raw.splitlines():
    h=line.strip()
    if not h: continue
    b=bytes.fromhex(h)
    if len(b)<7 or b[0:4]!=b'\x4f\x45\x74\x03': continue  # signature Minetest
    parse(b[7:], b[6])

# 2) Reconstituer les nodes du flag (id 54) + restaurer les positions cassées
solid=set()
for (bx,by,bz),p0 in blocks.items():
    for i,c in enumerate(p0):
        if c==FLAG_NODE:
            lz,r=divmod(i,256); ly,lx=divmod(r,16)
            solid.add((bx*16+lx, by*16+ly, bz*16+lz))
solid |= set(removed)                                     # popbob a cassé des nodes du flag -> les remettre

# 3) Façade X=-357, projection Y-Z (Z inversé = lecture à l'endroit) -> PNG
pts=[(x,y,z) for (x,y,z) in solid if x==FACE_X and 11<=y<=25]
ys=[p[1] for p in pts]; zs=[p[2] for p in pts]
ymin,ymax=min(ys),max(ys); zmin,zmax=min(zs),max(zs); W=zmax-zmin+1; H=ymax-ymin+1
proj=set((y, W-1-(z-zmin)) for (x,y,z) in pts)
S=9; PAD=2; grid=[[255]*(W+2*PAD) for _ in range(H+2*PAD)]
for (y,c) in proj: grid[(ymax-y)+PAD][c+PAD]=0
BW,BH=(W+2*PAD)*S,(H+2*PAD)*S; buf=bytearray()
for r in range(BH):
    buf.append(0); srow=grid[r//S]; buf.extend(bytes(srow[c//S] for c in range(BW)))
def chunk(t,dd): cc=t+dd; return struct.pack('>I',len(dd))+cc+struct.pack('>I',zlib.crc32(cc)&0xffffffff)
open("work/flag_solved.png","wb").write(
    b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',BW,BH,8,0,0,0,0))
    +chunk(b'IDAT',zlib.compress(bytes(buf),9))+chunk(b'IEND',b''))
print("OK -> work/flag_solved.png   (flag: uiuctf{BudG3t_c4ves_N_cl1fFs})")
