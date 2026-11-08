---
title: "Secret-Salad"
ctf: "Pwny-CTF"
category: "crypto"
difficulty: "Not specified"
points: 100
techniques: ["caesar-cipher", "osint"]
tools: ["cyberchef"]
keywords: ["Secret-Salad", "Pwny-CTF", "crypto", "caesar-cipher", "osint", "cyberchef"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Crypto/Secret-Salad/notes.md"
---

# Secret-Salad (Pwny-CTF, crypto)

## Summary
Challenge **Secret-Salad** from the Pwny-CTF CTF, crypto category. Main technique: caesar-cipher. Salad + “dressing” -> Caesar. An all-lowercase password among "realistic" passwords reveals simple ciphertext.

## Statement and artefacts
We have intercepted a crucial document via email. It appears to contain a list of usernames and their corresponding passwords for a website. If it helps, we have a screenshot of a blog post that our person of interest made. Can you help us recover their password?

**author**: Sophia

**Provided files / artifacts:**
- `image.png (image, 1.1 MB)`
- `passwords.txt (text, 713 B)`
- `unveil.txt (text, 86.5 KB)`
- `users.txt (text, 558 B)`

## Recognition signals
- Signal: Trap: several identical passwords (decoys); the right line is chosen by the OSINT index (the image), not at random.

## Resolution method
1. `users.txt` (34) and `passwords.txt` (34) are **line-aligned** (index 1) — `paste` to put them side by side.
2. The image = blog post *"In the Mountains"* / Patagonia → the user is **`wanderlust_and_mountains`** (clue 2: username linked to what he is looking at).
3. His password `jhlzhy_pz_tf_mhc_zhshk` is the **only one in lowercase letters** (the others = real random passwords with numbers/symbols = decoys).
4. Clue 4 *"classic special dressing to my salads"* → **Caesar sauce → Caesar figure**. Bruteforce of the 26 shifts → shift **−7** gives `caesar_is_my_fav_salad` (clear is self-confirming).
5. Flag = `sigpwny{` + clear + `}`.

## Discarded approaches
- Tools: dcode.fr “Caesar cipher” (bruteforce auto) · CyberChef “ROT13 Brute Force”.

## Flag
sigpwny{caesar_is_my_fav_salad}

## Lessons and reusable patterns
- Salad + “dressing” -> Caesar. An all-lowercase password among "realistic" passwords betrays simple ciphertext.
- Caesar = 26 possibilities -> always bruteforce the 26 and read the one who makes a word.
- Trap: several identical passwords (decoys); the right line is chosen from the OSINT clue (the image), not at random.
