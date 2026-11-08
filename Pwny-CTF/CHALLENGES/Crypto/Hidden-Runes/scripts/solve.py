# Hidden-Runes — Pwny-CTF (script de solve)
import collections

mapping = {"♅":"s", "♇":"i", "♈":"g", "♊":"p", "♏":"w", "♃":"n", "♂":"y", "_":"_", "{":"{", "}":"}","♐":"r", "☽":"v", "☾":"e","♀":"m","♌":"d","♑":"f","♒":"u","♄":"l","☉":"h","♍":"b", "♎":"t", "♋":"c", "♆":"a"}

with open("../mysterious_message.txt", "r") as f:
    content = f.read().strip().split()

flag_enc = content[-1]

content.pop()
symboles = []
for mot in content:
    for char in mot:
        symboles.append(char)


symboles = set(symboles) - set(" .!,'{}\n")

for i in range(len(flag_enc)):
    print(flag_enc[i], end=" ")

flag = []
print("\n")
for i in range(len(flag_enc)):
    dec = mapping.get(flag_enc[i], "*")
    flag.append(dec)

print(''.join(flag))