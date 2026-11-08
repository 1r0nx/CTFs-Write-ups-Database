# Cold-Chain — hiCTF (script de solve)
import time, sys
sys.path.insert(0,'/workspace/hiCTF/hardware/Cold-Chain/work')
from clmp import C
c=C(); print('serial',c.serial); print('AUTH',c.auth())
def run(cmd):
    print(f'>>> {cmd}')
    out=c.send(cmd)
    for l in out: print('   ',l)
    return out
run('MACRO GET M2'); run('SCHED GET S9')
print('\n--- CORRECTIF ---')
run('MACRO DISABLE M2')      # stoppe la persistance
run('SCHED SET S9 enabled=0')# neutralise le forçage
run('MACRO LIST'); run('SCHED LIST')
print('\n--- SURVEILLANCE ---')
t0=time.time()
while time.time()-t0 < 240:
    st=c.send('STATUS')
    temps=[l for l in c.send('CASES') if l.startswith('DATA')]
    tmax=max(float(x.split('temp=')[1].split()[0]) for x in temps) if temps else None
    line=[l for l in st if l.startswith('DATA')]
    print(f'[{int(time.time()-t0):3}s] tmax={tmax} | {line[0] if line else st}')
    if any('flag=' in l for l in st):
        for l in st:
            if 'flag=' in l: print('\n*** ',l)
        break
    if any('compliant=1' in l for l in st):
        print('compliant mais pas encore de flag, on continue'); 
    time.sleep(8)
c.close()
