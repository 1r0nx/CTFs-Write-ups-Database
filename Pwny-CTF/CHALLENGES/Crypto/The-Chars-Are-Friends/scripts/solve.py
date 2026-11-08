#!/usr/bin/env python3
# The Chars Are Friends (Pwny-CTF, Crypto)
#
# "OTP maison" : hide(c) = ord(c) ^ (random_byte & 0xc0).
# Le masque 0xc0 = 1100_0000 : SEULS les 2 bits de poids fort sont XORes avec de
# l'aleatoire. Les 6 bits de poids faible du caractere sont INTACTS. Or les
# caracteres d'un flag ASCII (lettres/chiffres/_{}) sont presque tous distinguables
# par leurs 6 bits bas -> on restaure les 2 bits hauts pour retomber sur un
# caractere de flag valide. (Le one-time pad n'est sur que s'il couvre TOUT le bit.)
import string

cipher = [51,105,231,176,55,46,185,187,50,225,174,228,111,237,223,105,51,174,180,
          95,33,181,52,239,45,97,52,41,163,97,172,236,249,31,51,37,163,181,242,229,253]

# charset du flag, en preferant lettres/symboles aux chiffres pour lever l'ambiguite
pref = string.ascii_letters + "_{}" + string.digits
out = []
for c in cipher:
    low = c & 0x3f                                  # 6 bits bas = conserves
    cands = {chr(low | m) for m in (0x00, 0x40, 0x80, 0xc0)}
    out.append(next(ch for ch in pref if ch in cands))   # 1er candidat valide
print("".join(out))
