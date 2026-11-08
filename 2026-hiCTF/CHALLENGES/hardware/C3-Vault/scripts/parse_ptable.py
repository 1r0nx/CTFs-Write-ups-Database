# C3-Vault — hiCTF (script de solve)
import struct, sys
d=open(sys.argv[1],'rb').read()
TYPES={0:'app',1:'data'}
SUB={(0,0):'factory',(0,0x10):'ota_0',(0,0x11):'ota_1',(1,0):'otadata',(1,1):'phy',(1,2):'nvs',
     (1,3):'coredump',(1,4):'nvs_keys',(1,5):'efuse',(1,0x80):'undefined',(1,0x81):'fat',(1,0x82):'spiffs'}
print(f'{"name":16} {"type":5} {"sub":10} {"offset":>10} {"size":>10}')
for i in range(0,len(d),32):
    e=d[i:i+32]
    if e[:2]!=b'\xaa\x50':
        if e[:2]==b'\xeb\xeb' or e[:2]==b'\xff\xff': break
        continue
    t,st=e[2],e[3]
    off,size=struct.unpack('<II',e[4:12])
    name=e[12:28].split(b'\x00')[0].decode('latin1')
    flags=struct.unpack('<I',e[28:32])[0]
    print(f'{name:16} {t:#04x}  {SUB.get((t,st),hex(st)):10} {off:#10x} {size:#10x}  flags={flags:#x}')
