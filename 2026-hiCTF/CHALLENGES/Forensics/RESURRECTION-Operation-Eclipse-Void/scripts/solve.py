# RESURRECTION: Operation Eclipse Void — extraction des 5 segments depuis l'image brute.
#
# Prérequis : The Sleuth Kit (fls/icat/istat) et une COPIE de travail de resurrection.raw.
# Le script répare la géométrie sur la copie (copie du boot sector de secours au début de la partition).
#
# Usage : python3 solve.py /chemin/vers/copie/resurrection.raw
import sys, struct, subprocess, re

IMG = sys.argv[1]
PART = 32768                         # LBA de début de la partition (GPT de secours, entrée 1)
OFF = str(PART)

# 0) Géométrie : MBR + GPT primaire + boot sector NTFS effacés ; GPT de secours et boot sector
#    de secours (dernier secteur de la partition, LBA 2093055) intacts -> on recopie le second.
with open(IMG, 'r+b') as f:
    f.seek(2093055 * 512); bs = f.read(512)
    assert bs[3:11] == b'NTFS    '
    f.seek(PART * 512); f.write(bs)

icat = lambda ino: subprocess.run(['icat', '-o', OFF, IMG, str(ino)], capture_output=True).stdout
istat = lambda ino: subprocess.run(['istat', '-o', OFF, IMG, str(ino)], capture_output=True, text=True).stdout
def mft_record(n):
    """Enregistrement MFT n, fixups appliqués."""
    r = bytearray(icat(0)[n * 1024:(n + 1) * 1024])
    uo, un = struct.unpack('<HH', r[4:8]); usn = r[uo:uo + 2]
    for i in range(1, un):
        p = i * 512 - 2
        if r[p:p + 2] == usn: r[p:p + 2] = r[uo + 2 * i:uo + 2 * i + 2]
    return r

segs = {}

# 1) Overlay PE de kbdusx.dll (MFT 179, horodatage falsifié) XORé avec son TimeDateStamp
dll = icat(179)
key = dll[0x88:0x8c]
segs[1] = bytes(c ^ key[i % 4] for i, c in enumerate(dll[0x400:]))[:42].decode()

# 2) Longueurs des fragments (runlist) du flux $DATA non nommé du dossier Confidential_Q3 (MFT 111)
r = mft_record(111); p = struct.unpack('<H', r[20:22])[0]; lens = []
while struct.unpack('<I', r[p:p + 4])[0] != 0xffffffff:
    t, L = struct.unpack('<II', r[p:p + 8])
    if t == 0x80 and r[p + 8] == 1 and r[p + 9] == 0:
        q = p + struct.unpack('<H', r[p + 32:p + 34])[0]
        while r[q]:
            ls, os_ = r[q] & 15, r[q] >> 4
            lens.append(int.from_bytes(r[q + 1:q + 1 + ls], 'little')); q += 1 + ls + os_
    p += L
segs[2] = ''.join(map(chr, lens))

# 3) Écarts entre les horodatages du journal TxR (tx_journal.log, MFT 181) : écart - 9984
j = icat(181)
fts = [struct.unpack('<Q', j[i * 0x50 + 32:i * 0x50 + 40])[0] for i in range(34)]
segs[3] = ''.join(chr(fts[i + 1] - fts[i] - 9984) for i in range(33))

# 4) Valeurs de substitution BinXML (UInt32) d'un enregistrement de Security_Audit.evtx (MFT 193)
e = icat(193)
segs[4] = ''.join(chr(struct.unpack('<I', e[0x11cd + 4 * i:0x11d1 + 4 * i])[0]) for i in range(33))

# 5) Clusters marqués alloués dans $Bitmap mais n'appartenant à aucun fichier : écarts = ASCII
bm = icat(6); own = set()
for ino in range(257):
    for line in istat(ino).split('Attributes:')[-1].splitlines():
        if re.fullmatch(r'[\d ]+', line.strip() or 'x'): own.update(int(x) for x in line.split())
NCLUS = 257535                       # clusters du volume (fsstat) ; les bits au-delà = bourrage de $Bitmap
pts = [c for c in range(170000, NCLUS) if bm[c >> 3] >> (c & 7) & 1 and c not in own]
segs[5] = ''.join(chr(pts[i + 1] - pts[i]) for i in range(len(pts) - 1))

for k in sorted(segs): print(f'segment {k} : {segs[k]}')
parts = [segs[k].split('--', 1)[1] for k in sorted(segs)]
parts[0] = parts[0].removeprefix('hiCTF{')
print('\nFLAG :', 'hiCTF{' + ''.join(parts))
