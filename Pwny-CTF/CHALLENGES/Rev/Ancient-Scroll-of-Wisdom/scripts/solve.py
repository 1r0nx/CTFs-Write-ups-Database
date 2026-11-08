#!/usr/bin/env python3
# Ancient Scroll of Wisdom — reverse d'un programme wenyan-lang (文言).
#
# scroll.wy valide un flag de 24 caracteres (= floor(pi**e)+2 = 22+2). Pour chaque position i :
#   字 = ((flag.charCodeAt(i) * 2) - 妙文[i%2] + 戲數[i%3]) XOR 嬉數[i%4]
#   临 = abs(字 - 字_precedent)            (字_precedent = 0 au depart)
#   密文 = 密(临)  -> base-12 avec les 12 animaux du zodiaque, zero-padde a 5 chiffres (鼠=0)
# La concatenation des 临 (24 x 5 digits) doit egaler 答.
#
# Constantes :
#   妙文 = 彼年何年號()  -> "西元" (nom d'ere pour une date moderne ; verifie via l'interpreteur)
#   戲數 = "六十九" (les caracteres, pas la valeur 69) ; 嬉數 = "四百二十"
#   嬉數/戲數/妙文 sont indexes par i%4 / i%3 / i%2.
#
# On inverse : chaque 临 connu -> 字 = 字_prec ± 临 (ambiguite du abs), puis
#   charCode = (( 字 XOR 嬉數[i%4] ) + 妙文[i%2] - 戲數[i%3]) / 2.
# On leve l'ambiguite en ne gardant que les codepoints "texte" (ASCII + CJK + ponctuation CJK) ;
# la seule branche entierement lisible est le flag.

ZOD = "鼠牛虎兔龍蛇馬羊猴雞犬豕"
TARGET = ("牛猴雞兔兔鼠兔馬龍牛鼠猴雞虎馬鼠牛犬馬蛇牛龍牛馬犬虎犬兔龍蛇牛雞兔牛鼠鼠猴蛇犬羊牛龍犬雞虎龍兔"
          "羊犬羊龍兔豕雞馬虎蛇雞鼠兔牛兔兔牛鼠鼠雞馬雞羊牛豕鼠豕猴虎兔龍兔豕鼠虎猴蛇虎鼠兔雞牛雞鼠雞蛇馬馬"
          "鼠猴羊雞蛇鼠牛兔猴鼠鼠牛龍牛雞牛羊蛇蛇鼠牛牛牛豕牛")

A = [ord('西'), ord('元')]     # 妙文 = "西元"
BS, CS = "六十九", "四百二十"    # 戲數, 嬉數
B = lambda i: ord(BS[i % 3])
C = lambda i: ord(CS[i % 4])


def jsxor(a, b):               # XOR a la JavaScript (Int32 signe), comme l'interpreteur wenyan
    r = (a & 0xFFFFFFFF) ^ (b & 0xFFFFFFFF)
    return r - 0x100000000 if r >= 0x80000000 else r


def decode_target():           # 答 -> liste des 24 临 (groupes de 5 chiffres base-12)
    d = {c: i for i, c in enumerate(ZOD)}
    digs = [d[c] for c in TARGET]
    lin = []
    for k in range(0, len(digs), 5):
        v = 0
        for x in digs[k:k + 5]:
            v = v * 12 + x
        lin.append(v)
    return lin


def is_text(c):
    return (0x20 <= c <= 0x7E) or (0x3000 <= c <= 0x9FFF) or (0xFF00 <= c <= 0xFFEF)


def recover():
    lin = decode_target()
    sols = []

    def dfs(i, prev_zi, chars):
        if i == len(lin):
            sols.append("".join(chars))
            return
        for sign in (1, -1):
            zi = sign * lin[i] if i == 0 else prev_zi + sign * lin[i]
            val = jsxor(zi, C(i)) + A[i % 2] - B(i)
            if val % 2:                       # charCode doit etre entier -> val pair
                continue
            c = val // 2
            if is_text(c):
                dfs(i + 1, zi, chars + [chr(c)])

    dfs(0, 0, [])
    return sols


def reencode(flag):            # verification independante : re-chiffrer doit redonner 答
    def mi(n):
        return ZOD[n] if n < 12 else mi(n // 12) + ZOD[n % 12]
    out, prev = "", 0
    for i, ch in enumerate(flag):
        zi = jsxor(ord(ch) * 2 - A[i % 2] + B(i), C(i))
        d = abs(zi - prev)
        prev = zi
        s = mi(d)
        while len(s) != 5:
            s = "鼠" + s
        out += s
    return out


if __name__ == "__main__":
    cands = recover()
    # la bonne solution est la seule phrase bien formee : 西格普尼「 ... 。」  ("sigpwny「...。」")
    good = [f for f in cands
            if f.startswith("西格普尼「") and f.endswith("。」") and reencode(f) == TARGET]
    for f in good:
        print("FLAG:", f)
        assert reencode(f) == TARGET, "re-encode mismatch"
    print(f"({len(cands)} candidats lisibles, {len(good)} bien forme(s))")
