# PM-Hash — Pwny-CTF (script de solve)
import hashlib
import itertools
import string

TARGET = "9272c1d1f611c71643a9d5a59109feb9c51c03c7"
chunks = [TARGET[i:i+4] for i in range(0, len(TARGET), 4)]
CHARSET = string.printable[:94]  # digits + lettres + ponctuation

# Table pour les paires (2 caractères)
pair_table = {}
for a, b in itertools.product(CHARSET, repeat=2):
    pair = a + b
    h = hashlib.md5(pair.encode()).hexdigest()[:4]
    pair_table.setdefault(h, []).append(pair)

# Table pour un seul caractère (dernier bloc si longueur impaire)
single_table = {}
for a in CHARSET:
    h = hashlib.md5(a.encode()).hexdigest()[:4]
    single_table.setdefault(h, []).append(a)

candidates = []
for i, c in enumerate(chunks):
    is_last = (i == len(chunks) - 1)
    opts = list(pair_table.get(c, []))
    if is_last:
        opts += single_table.get(c, [])  # ajoute les candidats à 1 caractère
    print(f"bloc {i} ({c}) -> {len(opts)} candidat(s): {opts}")
    if not opts:
        print(f"[!] Toujours aucun candidat pour {c}, élargis encore le charset.")
        exit(1)
    candidates.append(opts)

count = 1
for c in candidates:
    count *= len(c)
print(f"[*] {count} mot(s) de passe possible(s)")

results = []
for combo in itertools.product(*candidates):
    pwd = ''.join(combo)
    recomputed = ''.join(
        hashlib.md5(pwd[i:i+2].encode()).hexdigest()[:4]
        for i in range(0, len(pwd), 2)
    )
    if recomputed == TARGET:
        results.append(pwd)

print(f"\n[+] {len(results)} mot(s) de passe valide(s):")
for r in results:
    print(repr(r))