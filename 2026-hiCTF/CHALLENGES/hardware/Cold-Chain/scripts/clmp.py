# Client CLMP/1.1 sur TLS (SNI) pour le CM-900.
import socket, ssl, hashlib, time
HOST='cold-chain-control-ae0a0b213e35.chall.hiddeninvestigations.net'; PORT=1337
KEY="CLNK-FIELD-MASTER-6E1D-DO-NOT-DISTRIBUTE"
def token(serial,nonce): return hashlib.sha256(f"{KEY}|{serial}|{nonce}".encode()).hexdigest()[:16]
class C:
    def __init__(self,host=HOST,port=PORT):
        ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
        self.s=ctx.wrap_socket(socket.create_connection((host,port),timeout=15),server_hostname=host)
        self.f=self.s.makefile('rwb',buffering=0); self.serial=self.nonce=None
        while True:
            l=self._rl()
            if l.startswith('SERIAL '): self.serial=l.split(None,1)[1].strip()
            elif l.startswith('NONCE '): self.nonce=l.split(None,1)[1].strip()
            elif l.startswith('OK') or l.startswith('ERR'): break
    def _rl(self):
        r=self.f.readline()
        if not r: raise ConnectionError('closed')
        return r.decode('utf-8','replace').rstrip('\n')
    def send(self,cmd):
        self.f.write((cmd+'\n').encode()); out=[]
        while True:
            l=self._rl(); out.append(l)
            if l.startswith('OK') or l.startswith('ERR'): break
        return out
    def auth(self):
        return self.send(f'AUTH {self.serial} {token(self.serial,self.nonce)}')
    def close(self):
        try: self.send('QUIT')
        except: pass
        try: self.s.close()
        except: pass
if __name__=='__main__':
    c=C(); print('serial',c.serial,'nonce',c.nonce)
    print('AUTH:', c.auth())
    for cmd in ['CASES','SCHED LIST','MACRO LIST','STATUS']:
        print(f'\n>>> {cmd}')
        for l in c.send(cmd): print('  ',l)
    c.close()
