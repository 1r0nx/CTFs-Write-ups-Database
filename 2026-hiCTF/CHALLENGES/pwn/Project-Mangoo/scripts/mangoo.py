# Project-Mangoo — hiCTF (script de solve)
import ssl, socket, re, sys
HOST="project-mangoo-d398c87957c2.chall.hiddeninvestigations.net"; PORT=1337
def rol8(v,n): return ((v<<n)|(v>>(8-n)))&0xFF
def token_for(ch):
    return bytes(((rol8(ch[i],3) ^ ((0x11*i)&0xFF) ^ 0x6a)&0xFF) for i in range(32))
class Conn:
    def __init__(self):
        ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
        s=socket.create_connection((HOST,PORT),timeout=10)
        self.s=ctx.wrap_socket(s,server_hostname=HOST); self.s.settimeout(8); self.buf=b""
    def recv_until(self,marker,tmo=8):
        self.s.settimeout(tmo)
        while marker not in self.buf:
            try: c=self.s.recv(4096)
            except Exception: break
            if not c: break
            self.buf+=c
        i=self.buf.find(marker)
        if i<0: out=self.buf; self.buf=b""; return out
        out=self.buf[:i+len(marker)]; self.buf=self.buf[i+len(marker):]; return out
    def send(self,d): self.s.sendall(d)
    def auth(self):
        d=self.recv_until(b"Authorization Token: ")
        m=re.search(rb"Session Challenge: ([0-9a-f]{64})",d)
        ch=bytes.fromhex(m.group(1).decode())
        self.send(token_for(ch).hex().encode()+b"\n")
        return self.recv_until(b"Option > ")
def query(c,channel):
    c.send(b"2\n")
    c.recv_until(b"Channel:")
    c.send(str(channel).encode()+b"\n")
    return c.recv_until(b"Option > ")

if __name__=="__main__":
    c=Conn()
    pre=c.auth()
    sys.stdout.write("=== après auth ===\n"+pre.decode('latin1',errors='replace')+"\n")
    for chn in (0,-1,-3,-2,1):
        r=query(c,chn)
        print(f"=== Query ch={chn} ===")
        print(r.decode('latin1',errors='replace').strip())
    c.send(b"5\n")  # terminate proprement
