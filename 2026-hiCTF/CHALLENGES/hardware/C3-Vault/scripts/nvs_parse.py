# Parseur NVS ESP-IDF. Chaque page = 4096 o : header 32 o, bitmap 32 o, 126 entrées de 32 o.
import sys, struct
data = open(sys.argv[1], 'rb').read()
start = int(sys.argv[2], 0); end = int(sys.argv[3], 0)
TYPES = {0x01:'U8',0x11:'I8',0x02:'U16',0x12:'I16',0x04:'U32',0x14:'I32',0x08:'U64',0x18:'I64',
         0x21:'STR',0x42:'BLOB',0x48:'BLOB_DATA',0x41:'BLOB_IDX',0x02:'U16'}
ns = {}   # index -> nom de namespace
blob_pending = {}
for page_off in range(start, end, 4096):
    page = data[page_off:page_off+4096]
    if len(page) < 4096: break
    state = struct.unpack('<I', page[0:4])[0]
    seq = struct.unpack('<I', page[4:8])[0]
    ver = page[8]
    bitmap = page[32:64]
    statename = {0xFFFFFFFF:'EMPTY',0xFFFFFFFE:'ACTIVE',0xFFFFFFFC:'FULL',0xFFFFFFF8:'FREEING',0x00000000:'CORRUPT'}.get(state,hex(state))
    print(f'\n== PAGE @{page_off:#x} state={statename} seq={seq} ver={ver:#x} ==')
    i = 0
    while i < 126:
        # état de l'entrée : 2 bits par entrée dans le bitmap
        bs = (bitmap[i//4] >> ((i%4)*2)) & 3   # 3=empty,2=written,0=erased
        e = page[64+i*32:64+i*32+32]
        nsidx, typ, span, chunk = e[0], e[1], e[2], e[3]
        crc = struct.unpack('<I', e[4:8])[0]
        key = e[8:24].split(b'\x00')[0]
        if bs == 2 and typ in TYPES:  # écrite
            tname = TYPES.get(typ, hex(typ))
            if typ == 0x01 and key==b'' and nsidx==0:
                pass
            if nsidx == 0:  # entrée de namespace : data = index
                nsval = e[24]
                ns[nsval] = key.decode('latin1','replace')
                print(f'  [{i:3}] NS-DEF idx={nsval} name={key!r}')
            else:
                nsname = ns.get(nsidx, f'ns#{nsidx}')
                if tname in ('STR','BLOB','BLOB_DATA'):
                    size = struct.unpack('<H', e[24:26])[0]
                    dcrc = struct.unpack('<I', e[28:32])[0]
                    # données dans les entrées suivantes
                    dstart = 64+(i+1)*32
                    blob = page[dstart:dstart+size]
                    print(f'  [{i:3}] ns={nsname!r} key={key.decode("latin1")!r} type={tname} size={size} chunk={chunk}')
                    print(f'        data={blob[:64].hex()}  ascii={blob[:48]!r}')
                    i += span-1
                else:
                    val = struct.unpack('<Q', e[24:32])[0]
                    print(f'  [{i:3}] ns={nsname!r} key={key.decode("latin1")!r} type={tname} val={val} ({val:#x})')
        i += 1
print('\nNamespaces:', ns)
