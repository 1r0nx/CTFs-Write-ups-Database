---
title: "Layer-7"
ctf: "Pwny-CTF"
category: "network"
difficulty: "hard"
points: 75
techniques: ["jwt", "pcap-analysis", "ftp", "dns", "encoding"]
tools: ["wireshark", "tshark"]
keywords: ["Layer-7", "Pwny-CTF", "network", "jwt", "pcap-analysis", "ftp", "dns", "encoding", "wireshark", "tshark", "pcap", "png", "http", "https", "aes", "base64"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Networking/Layer-7/notes.md"
---

# Layer-7 (Pwny-CTF, network)

## Summary
Challenge **Layer-7** from the Pwny-CTF CTF, network category. Main technique: jwt. When there is neither login page nor Authorization header, look at all the headers (http.request.line), in particular Cookie: — auth can be stored there.

## Statement and artefacts
Use Wireshark to open `layers.pcap` and complete the challenge. The file is the same from `Layer 1`.

Layer 7 represents the application layer of the OSI model, which includes protocols like HTTP, DNS, FTP, SSH, and more!

The flag is the password used to authenticate with the HTTP web server.

**Author**: Minh

## Recognition signals
- When there is neither login page nor Authorization header, look at all the headers (http.request.line), in particular Cookie: — auth can be stored there.

## Resolution method
1. List HTTP requests — `tshark -r../layers.pcap -Y 'http.request' -T fields -e http.request.method -e http.host -e http.request.uri` → server `nftgallery.local`, no login page (only `GET /images/*.png`).
2. Rule out false leads: no form POST (the only POST is **OCSP**), no `Authorization` header (empty `http.authorization`), no `WWW-Authenticate` or 401 → no “classic” HTTP auth.
3. Dump **all header lines** of requests — `tshark... -T fields -e http.request.line` → presence of a `Cookie: auth=eyJ1c2VyIjogImVsb24i...`.
4. Decode base64 — `echo "eyJ1c2VyIjogImVsb24iLCBwYXNzd29yZDoibDF0dGwzWEBFQS0hMiJ9" | base64 -d` → `{"user": "elon", password:"l1ttl3X@EA-!2"}`.
5. Flag = the password, in series format: `sigpwny{l1ttl3X@EA-!2}`.

1. **More difficult variation**

In competitive CTF, the cookie could be:
- a signed **JWT** (`header.payload.signature`) where only the payload is in base64url (readable), the signature preventing it from being forged without the key;
- an **encrypted** value (AES) and not just encoded → the key would have to be found elsewhere in the capture;
- placed on **HTTPS** → you would need the TLS key (`SSLKEYLOGFILE` file) to decrypt before seeing the cookie.

## Flag
sigpwny{l1ttl3X@EA-!2}

## Lessons and reusable patterns
- When there is neither login page nor Authorization header, look at all the headers (http.request.line), in particular Cookie: — auth can be stored there.
- Base64 reflex: a value that starts with eyJ = base64 encoded JSON ({"...). base64 -d to read.
- Useful red herrings to know: an OCSP POST (ocsp.pki.goog) is not a login, it is TLS certificate verification; it pollutes a filter http.request.method == "POST".
- Base64 = encoding, not encryption -> always reversible. A “base64” secret is not protected.
