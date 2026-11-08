# Warden’s-Maze — hiCTF (script de solve)
from pwn import *
import re, collections, time
context.log_level='error'
import sys
HOST=sys.argv[1] if len(sys.argv)>1 else "maze-breach-426afe80ec38.chall.hiddeninvestigations.net"
PORT=int(sys.argv[2]) if len(sys.argv)>2 else 1337
io=remote(HOST,PORT,ssl=True,sni=HOST)
def frame(maxwait=4.0):
    data=b""; deadline=time.time()+maxwait
    while time.time()<deadline:
        try: c=io.recv(timeout=0.5)
        except EOFError: return data.decode('latin1','replace')
        if c: data+=c; deadline=time.time()+0.3
        elif data: break
    return data.decode('latin1','replace')
def parse(txt):
    txt=re.sub(r'\x1b\[[0-9;]*[A-Za-z]','\n',txt)
    g=[]
    for ln in txt.split('\n'):
        t=ln.rstrip('\r')
        if t.startswith('  ') and re.fullmatch(r'[#@G%\$ .]{22,26}', t[2:]): g.append(t[2:])
    return g
def find(g,ch):
    for y,r in enumerate(g):
        x=r.find(ch)
        if x>=0: return (y,x)
DIR=[('w',-1,0),('s',1,0),('a',0,-1),('d',0,1)]; cp=lambda c:c in ' .$'
def bfs(g,s0,goal,avoid):
    q=collections.deque([(s0,"")]);seen={s0}
    while q:
        (y,x),p=q.popleft()
        if (y,x)==goal:return p
        for k,dy,dx in DIR:
            ny,nx=y+dy,x+dx
            if 0<=ny<len(g) and 0<=nx<len(g[ny]) and (ny,nx) not in seen and (ny,nx)!=avoid and cp(g[ny][nx]):
                seen.add((ny,nx));q.append(((ny,nx),p+k))
    return None
BREACH=(14,4); breached=False; log=open('solve.log','w')
def P(*a): print(*a); print(*a,file=log); log.flush()
txt=frame(5.0)
g=parse(txt); P("bannière lignes:",len(g))
if g: P('\n'.join(g))
for step in range(250):
    if 'hiCTF{' in txt:
        P("\n*** FLAG:",re.search(r'hiCTF\{[^}]*\}',txt).group()); break
    g=parse(txt)
    if not g: P("no-grid, extrait:",repr(txt[:80])); txt=frame(2.0); continue
    me=find(g,'@'); war=find(g,'G'); dol=find(g,'$')
    if (len(g)>9 and len(g[9])>12 and g[9][12] in ' .') or (me and me[0]>=9 and me[1] in (11,12,13) and me[0]<=14): breached=True
    wopen=breached
    if me is None: io.send(b'd\n'); txt=frame(); continue
    goal= dol if (wopen and dol) else ((10,12) if wopen else BREACH)
    path=bfs(g,me,goal,war) or bfs(g,me,goal,None)
    mv=path[0] if path else 'w'
    if step<4 or wopen or step%10==0: P(f"s{step} me={me} G={war} goal={goal} open={wopen} mv={mv}")
    io.send((mv+'\n').encode()); txt=frame(1.2)
io.close(); log.close()
