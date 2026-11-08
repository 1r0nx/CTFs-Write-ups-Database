# Warden’s-Maze — hiCTF (script de solve)
import collections
GRID="""########################
#.    .    .P   .    . #
# .    .    .    .    .#
###.####.####### #### ##
#   .    .    .    .   #
#    .    .    .    .  #
######.####.###### ### #
# .    .    .    .    .#
#  .    .    .    .    #
## #### #======## ## ###
#    .   =----=.    .  #
#.    .  =-*--= .    . #
### #### =----=# #### ##
#  .#   .=----=   .    #
#   .    ======    .   #
#### # #### ###### ### #
#.    .    .    .    . #
# .    .    .    .    .#
## # ## ######### ## ###
#   .    . G  .    .   #
#### ###################"""
rows=GRID.split("\n"); H=len(rows); W=len(rows[0])
CODE={'#':1,'.':2,'=':3,'-':4,'*':5,' ':0,'P':0,'G':0}
# carte initiale (octets)
m=bytearray(W*H)
pr=pc=None
for y,r in enumerate(rows):
    for x,c in enumerate(r):
        m[y*W+x]=CODE[c]
        if c=='P': pr,pc=y,x
start=(pr,pc)
# prix
for y in range(H):
    for x in range(W):
        if rows[y][x]=='*': prize=(y,x)
def player_passable(b):
    code=b&0x3f
    return code<=5 and ((0x35>>(b&0x1f))&1)==1
def opaque(b):  # bloque la vue : (tile&0x3f)|2 == 3  -> code 1 ou 3
    return ((b&0x3f)|2)==3
def reveal(m,pr,pc):
    m=bytearray(m)
    for dy in range(-6,7):
        ady=abs(dy)
        row=pr+dy
        for dx in range(-6,7):
            if dx*dx+dy*dy>=0x25: continue
            col=pc+dx
            if not(0<=row<H and 0<=col<W): continue
            # LOS : algo du binaire simplifié -> on marche en ligne de (pr,pc) vers (row,col)
            if not line_of_sight(m,pr,pc,row,col): continue
            read=m[col+W*row]
            # index d'écriture bugué : int8(dx+24*dy) + base
            off=(dx+W*dy)
            off=((off+128)&0xff)-128   # troncature int8 signé
            wi=pr*W+pc+off
            if 0<=wi<W*H:
                m[wi]=(read&0x3f)|0x40
    return m
def line_of_sight(m,pr,pc,row,col):
    # Bresenham supercover approx : si une cellule intermédiaire (hors extrémités) est opaque -> bloqué
    dx=col-pc; dy=row-pr
    n=max(abs(dx),abs(dy))
    if n==0: return True
    for i in range(1,n):
        x=pc+round(dx*i/n); y=pr+round(dy*i/n)
        if (y,x)==(pr,pc) or (y,x)==(row,col): continue
        if opaque(m[y*W+x]): return False
    return True
DIRS={'w':(-1,0),'s':(1,0),'a':(0,-1),'d':(0,1)}
# BFS sur (pos, carte) ; appliquer reveal à chaque pas
startm=reveal(m,pr,pc)
seen={(start,bytes(startm))}
q=collections.deque([(start,startm,"")])
ans=None
while q:
    (y,x),cm,path=q.popleft()
    if len(path)>60: continue
    for k,(ddy,ddx) in DIRS.items():
        ny,nx=y+ddy,x+ddx
        if not(0<=ny<H and 0<=nx<W): continue
        b=cm[ny*W+nx]
        if not player_passable(b): continue
        code=b&0x3f
        nm=bytearray(cm)
        if code==2: nm[ny*W+nx]=0x40
        if code==5:
            ans=path+k; print("WIN séquence:",ans,"longueur",len(ans)); q.clear(); break
        nm=reveal(nm,ny,nx)
        key=((ny,nx),bytes(nm))
        if key not in seen:
            seen.add(key); q.append(((ny,nx),nm,path+k))
print("start",start,"prize",prize)
