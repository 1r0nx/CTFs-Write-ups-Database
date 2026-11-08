#!/usr/bin/env python3
# chal.py = exec(base64(...)) d'un quiz obfusqué ("screaming" : chaque variable est une
# suite de 'A' de longueur unique). input() est redéfini : chaque réponse alimente un
# accumulateur global comparé à la fin à une constante.
# Pour "What is the flag?", le handler ne renvoie rien (None) -> chaque caractère fait
#   acc = (acc << 8) + transform(ord(c))
# transform est une bijection fixe sur les octets ; il suffit de l'inverser sur la constante.

perm = [58,143,247,197,216,64,41,71,239,141,76,124,144,66,151,204,192,69,129,6,84,184,9,
        248,61,20,31,136,130,87,55,96,115,85,90,39,98,254,228,44,234,138,225,43,108,21,35,
        23,233,0,134,150,72,227,146,180,7,132,15,42,4,152,200,193,244,199,83,26,33,122,14,
        16,127,198,32,120,77,241,68,133,30,232,155,236,203,24,240,40,173,53,92,253,145,46,
        89,75,154,205,207,206,164,119,219,95,194,99,226,231,147,157,123,19,215,163,45,97,51,
        56,245,214,202,166,67,22,102,54,59,179,109,2,168,210,167,94,27,82,126,28,78,73,246,
        79,230,252,186,117,5,218,176,237,81,250,50,185,160,224,195,188,74,135,212,196,12,80,
        175,37,29,125,65,222,249,172,217,104,88,243,178,34,38,13,189,229,25,91,111,60,148,
        128,153,36,174,161,177,169,48,139,103,112,235,251,165,18,238,201,213,63,162,156,171,
        49,116,107,191,211,1,208,113,242,100,105,220,183,86,190,47,187,159,70,17,221,110,121,
        181,8,182,131,158,101,3,149,11,57,52,10,106,140,223,255,209,142,170,137,93,114,118,62]

# le combinateur S(S) du challenge applique sa fonction 4 fois
apply4 = lambda f: (lambda x: f(f(f(f(x)))))

v27 = lambda x: (x * 2) & 0x1e
v28 = lambda x: (-16) & (((((x + 23) % 256 - 23) % 256) * 2) - x)   # ~0xF = -16, 0xAA+0x56 = 256
v30 = lambda x: v28(x) | (v27(x) // 2)
v26 = lambda x: x ^ 3 ^ 0x38
v29 = apply4(lambda x: perm[x])            # perm appliquée 4x


def transform(b):
    y = v26(b)
    y = apply4(v30)(y)                      # v30 appliquée 4x
    y = apply4(v29)(y)                      # v29 appliquée 4x -> perm 16x
    return y & 0xFF


def main():
    inv = {transform(b): b for b in range(256)}   # bijection -> table inverse
    target = 0xf09c336cf123302a1b7a6ddbde7947b352bc7c0fbc1116f493bcf6804766f4114f3980de5dcb168711bc5900
    tb = target.to_bytes((target.bit_length() + 7) // 8, "big")
    decoded = "".join(chr(inv[x]) for x in tb[:-1])   # on retire le 00 final (<<8 de fin)
    print("Décodé :", decoded)
    i = decoded.find("sigpwny{")
    print("Flag   :", decoded[i:] if i >= 0 else "(non trouvé)")


if __name__ == "__main__":
    main()
