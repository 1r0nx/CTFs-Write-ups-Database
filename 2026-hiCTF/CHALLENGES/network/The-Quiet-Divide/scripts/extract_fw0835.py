# The-Quiet-Divide — hiCTF (script de solve)
import subprocess, hashlib, re
PCAP="/tmp/claude-0/-workspace/4f82a184-2b70-44f2-a1a7-848979c256e1/scratchpad/tqd/the-quiet-divide/the-quiet-divide.pcap"
# flux candidats vers .35:8085 qui ne sont PAS /v2/manifest
streams=[10,11,12,13,25,47,53,59,65,74]
buf=bytearray(14528)
filled=[False]*14528
for s in streams:
    out=subprocess.run(["tshark","-r",PCAP,"-Y",f"tcp.stream=={s} && ip.src==10.77.40.35",
                        "-T","fields","-e","tcp.payload"],capture_output=True,text=True).stdout
    hexstr="".join(out.split())
    if not hexstr: continue
    raw=bytes.fromhex(hexstr)
    # separer entete/corps HTTP
    idx=raw.find(b"\r\n\r\n")
    if idx<0: continue
    head=raw[:idx].decode('latin1'); body=raw[idx+4:]
    m=re.search(r"Content-Range: bytes (\d+)-(\d+)/(\d+)",head)
    if not m:
        print(f"stream {s}: pas de Content-Range; head[:60]={head[:60]!r}"); continue
    lo,hi,total=int(m.group(1)),int(m.group(2)),int(m.group(3))
    seg=body[:hi-lo+1]
    buf[lo:lo+len(seg)]=seg
    for i in range(lo,lo+len(seg)): filled[i]=True
    print(f"stream {s}: range {lo}-{hi}/{total}  ({len(seg)} o)")
print("octets manquants:", filled.count(False))
h=hashlib.sha256(bytes(buf)).hexdigest()
print("sha256 =", h)
print("attendu 0835dfce789d002d55f3d20fe7f953a30da0adbef336a861839ce8f579958836")
if h.startswith("0835dfce"):
    open("/tmp/claude-0/-workspace/0d9ec413-ed3a-454d-9f5e-b53392f82479/scratchpad/firmware_0835.bin","wb").write(bytes(buf))
    print("OK -> firmware_0835.bin")
