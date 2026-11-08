# TESSERA — reconstruit les 3 parties du flag à partir de la collecte extraite.
#
# Usage : python3 solve.py <dossier "evidence" extrait de tessera.zip>
# Prérequis : impacket (dpapi.py dans le PATH), pycryptodome, mft (pip install mft)
#
#  1) ETW : AuditDiagTrace.etl (fournisseur Microsoft-Windows-Diagnostics-LpcEndpoint)
#           contient "PORT=\RPC Control\AepLocalEndpoint_Q8;HEX=..." ; HEX XORé 0x5A
#  2) DPAPI machine : service factice DiagTrackSvcAux -> ServiceVault (cpinforev.dat)
#           + EntropyToken (Base64 de "TesseraEntropy_99") ; clé maître via SYSTEM+SECURITY
#  3) Point d'analyse NTFS (tag 0xA0000028) sur ProgramData\Microsoft\Diagnosis\ETLLocalStore,
#           données = AES-256-CBC(NextKey, IV) -> lu dans l'enregistrement MFT (résident)
import sys, os, re, json, struct, base64, subprocess
from Crypto.Cipher import AES

E = sys.argv[1]
J = lambda *p: os.path.join(E, *p)

# ---------- 1) ETL : événement « LPC » ----------
etl = open(J('Windows/System32/LogFiles/WMI/AuditDiagTrace.etl'), 'rb').read()
hexs = re.search(rb'H\x00E\x00X\x00=\x00((?:[0-9A-F]\x00)+)', etl).group(1)[::2].decode()
msg1 = bytes(b ^ 0x5A for b in bytes.fromhex(hexs)).decode()
part1_raw, clue = msg1.split('||')
print('[1]', msg1)

# ---------- 2) DPAPI (portée machine) ----------
C = J('Windows/System32/config')
blob = J('Windows/System32/config/systemprofile/AppData/Local/Microsoft/Windows/Caches/cpinforev.dat')
mk_guid = str(__import__('uuid').UUID(bytes_le=open(blob, 'rb').read()[24:40]))
mk = J('Windows/System32/Microsoft/Protect/S-1-5-18', mk_guid)
out = subprocess.run(['dpapi.py', 'masterkey', '-file', mk, '-system', J(C, 'SYSTEM'), '-security', J(C, 'SECURITY')],
                     capture_output=True, text=True).stdout
key = re.search(r'Decrypted key: (0x[0-9a-f]+)', out).group(1)
entropy = base64.b64decode('VGVzc2VyYUVudHJvcHlfOTk=').decode()      # valeur EntropyToken du registre
out = subprocess.run(['dpapi.py', 'unprotect', '-file', blob, '-key', key, '-entropy', entropy],
                     capture_output=True, text=True).stdout
pt = bytes(int(h, 16) for l in out.splitlines() if re.match(r'^ [0-9a-f]{4} ', l)
           for h in re.findall(r'\b[0-9A-F]{2}\b', l[7:56]))
vault = json.loads(pt)
print('[2]', vault['FlagPart2'])

# ---------- 3) Point d'analyse NTFS chiffré ----------
import mft
p = mft.PyMftParser(J('[SYSTEM]', '$MFT'))
for e in p.entries():
    if isinstance(e, RuntimeError): continue
    if (e.full_path or '').lower().endswith('microsoft\\diagnosis\\etllocalstore'):
        rp = next(bytes(a.raw_value) for a in e.attributes()
                  if not isinstance(a, RuntimeError) and a.type_code == 0xC0)
        break
tag, dl = struct.unpack('<IH', rp[:6])
data = rp[8:8 + dl]
k3 = vault['NextKey'].encode().ljust(32, b'0')[:32]
dec = AES.new(k3, AES.MODE_CBC, bytes.fromhex(vault['IV_HEX'])).decrypt(data)
part3_raw = dec[:-dec[-1]].decode()                                     # retrait du bourrage PKCS#7
print(f'[3] tag=0x{tag:08X}', part3_raw)

# ---------- Assemblage : on garde ce qui suit le dernier groupe de tirets ----------
payload = lambda s: re.split(r'-{2,}', s)[-1]
p1, p2, p3 = payload(part1_raw), payload(vault['FlagPart2']), payload(part3_raw)
print('\nFLAG :', p1 + p2 + p3)
