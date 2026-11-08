# Génère data.h (constantes pour cairn.c) à partir de challenge.json
import sys, json
d = json.load(open(sys.argv[1]))
p = d["p"]; assert p == 2**256 - 2**32 - 977
def limbs(x): return "{{0x%016xULL,0x%016xULL,0x%016xULL,0x%016xULL}}" % tuple((x >> (64*k)) & (2**64-1) for k in range(4))
out = []
for l in d["L"]:
    t = d["phi"][str(l)]
    out.append("static const term PHI%d[] = {%s};" % (l, ",".join("{%d,%d,%s}" % (xe, ye, limbs(c % p)) for xe, ye, c in t)))
    out.append("#define NPHI%d %d" % (l, len(t)))
# racines 42-ièmes de l'unité dans GF(p)
m = 42
for g in range(2, 1000):
    z = pow(g, (p-1)//m, p)
    if all(pow(z, m//q, p) != 1 for q in (2, 3, 7)): break
mu = [pow(z, k, p) for k in range(m)]
out.append("static const fp MU[%d] = {%s};" % (m, ",".join(limbs(x) for x in mu)))
out.append("static const fp E1 = %s;" % limbs((p-1)//m))          # (p-1)/42
out.append("static const fp PM2 = %s;" % limbs(p-2))              # p-2 (inversion)
H = (p*p-1)//2
out.append("static const uint64_t EH[8] = {%s};" % ",".join("0x%016xULL" % ((H >> (64*k)) & (2**64-1)) for k in range(8)))
out.append("static const uint8_t SALT[32] = {%s};" % ",".join(str(b) for b in bytes.fromhex(d["salt_hex"])))
out.append("static const fp J0A = %s, J0B = %s;" % (limbs(d["j0"][0]), limbs(d["j0"][1])))
out.append("#define TSTEPS %d" % d["T"])
open(sys.argv[2], "w").write("\n".join(out) + "\n")
