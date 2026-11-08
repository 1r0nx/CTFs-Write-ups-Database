#!/usr/bin/env python3
# LLL ENTIER (Cohen, "A Course in Computational Algebraic Number Theory", Algo 2.6.7)
# + Coppersmith univarie. Arithmetique entiere -> rapide meme en grandes dimensions.
def lll_int(B):
    B=[list(map(int,row)) for row in B]
    n=len(B)
    def dot(u,v): return sum(a*b for a,b in zip(u,v))
    d=[1]*(n+1)
    lam=[[0]*n for _ in range(n)]
    # Gram-Schmidt entier initial
    for i in range(n):
        for j in range(i+1):
            u=dot(B[i],B[j])
            for k in range(j):
                u=(d[k+1]*u - lam[i][k]*lam[j][k])//d[k]
            if j<i: lam[i][j]=u
            else: d[i+1]=u
    def REDI(k,l):
        if 2*abs(lam[k][l])<=d[l+1]: return
        q=(2*lam[k][l]+d[l+1])//(2*d[l+1])
        B[k]=[B[k][i]-q*B[l][i] for i in range(len(B[k]))]
        lam[k][l]-=q*d[l+1]
        for i in range(l):
            lam[k][i]-=q*lam[l][i]
    def SWAPI(k):
        B[k],B[k-1]=B[k-1],B[k]
        for j in range(k-1):
            lam[k][j],lam[k-1][j]=lam[k-1][j],lam[k][j]
        lk=lam[k][k-1]
        B_=(d[k-1]*d[k+1]+lk*lk)//d[k]
        for i in range(k+1,n):
            t=lam[i][k]
            lam[i][k]=(d[k+1]*lam[i][k-1]-lk*t)//d[k]
            lam[i][k-1]=(B_*t+lk*lam[i][k])//d[k+1]
        d[k]=B_
    k=1
    while k<n:
        REDI(k,k-1)
        # condition de Lovasz (version entiere, delta=3/4)
        if 4*d[k+1]*d[k-1] < 3*d[k]*d[k] - 4*lam[k][k-1]*lam[k][k-1]:
            SWAPI(k)
            k=max(k-1,1)
        else:
            for l in range(k-2,-1,-1): REDI(k,l)
            k+=1
    return B

def polymul(a,b):
    r=[0]*(len(a)+len(b)-1)
    for i,ai in enumerate(a):
        for j,bj in enumerate(b): r[i+j]+=ai*bj
    return r

def small_roots(fc,N,X,m=2,t=1):
    d=len(fc)-1
    fpw=[[1]]
    for _ in range(m+1): fpw.append(polymul(fpw[-1],fc))
    polys=[]
    for i in range(m):
        for j in range(d):
            polys.append([0]*j+[c*(N**(m-i)) for c in fpw[i]])
    for i in range(t):
        polys.append([0]*i+fpw[m][:])
    dim=d*m+t
    M=[[0]*dim for _ in range(dim)]
    for r,p in enumerate(polys):
        for k in range(min(len(p),dim)): M[r][k]=p[k]*(X**k)
    M=lll_int(M)
    g=[M[0][k]//(X**k) for k in range(dim)]
    while g and g[-1]==0: g.pop()
    return g

def roots_of(g,X):
    import sympy
    x=sympy.symbols('x')
    poly=sympy.Poly(sum(c*x**k for k,c in enumerate(g)),x)
    return [int(r) for r in poly.ground_roots() if r.is_integer and abs(int(r))<X]

if __name__=="__main__":
    from Crypto.Util.number import getPrime
    import random, sympy, time
    p=getPrime(2048); q=getPrime(2048); N=p*q
    x0=random.randint(0,256**40); A=int.from_bytes(b'\x01'*472,'big')*(256**40)
    ct=pow(A+x0,3,N)
    xs=sympy.symbols('x')
    fc=[c%N for c in [int(c) for c in sympy.Poly(sympy.expand((A+xs)**3-ct),xs).all_coeffs()[::-1]]]; fc[-1]=1
    t=time.time(); g=small_roots(fc,N,256**40,m=1,t=1)
    print("dim4 time",round(time.time()-t,2),"ok:",x0 in roots_of(g,256**40))
