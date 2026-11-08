# C3-Vault — hiCTF (script de solve)
import socket, ssl
def connect(host,port):
    ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
    s=ctx.wrap_socket(socket.create_connection((host,port),timeout=20))
    s.settimeout(6); buf=b''
    try:
        while b'CHALLENGE' not in buf or b'Commands' not in buf:
            d=s.recv(4096)
            if not d: break
            buf+=d
    except socket.timeout: pass
    return s,buf.decode(errors='replace')
def drain(s):
    s.settimeout(6); out=b''
    try:
        while True:
            d=s.recv(4096)
            if not d: break
            out+=d
    except socket.timeout: pass
    return out.decode(errors='replace')
