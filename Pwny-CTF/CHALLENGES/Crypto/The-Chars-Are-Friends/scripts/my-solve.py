# The-Chars-Are-Friends — Pwny-CTF (script de solve)
cipher_arr = [51, 105, 231, 176, 55, 46, 185, 187, 50, 225, 174, 228, 111, 237, 223, 105, 51, 174, 180, 95, 33, 181, 52, 239, 45, 97, 52, 41, 163, 97, 172, 236, 249, 31, 51, 37, 163, 181, 242, 229, 253]

candidat = [0x00,0x40,0x80,0xC0]
flag = []

for c in cipher_arr:
    for cand in candidat:
        tmp = c ^ cand
        test = chr(tmp)
        if test.isascii() or test.isdigit():
             flag.append(test)


print(''.join(flag))


# sigpwny{random_isnt_automatically_secure}