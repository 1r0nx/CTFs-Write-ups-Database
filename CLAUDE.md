# Base de write-ups CTF (interrogée avec `ctf-find`)

Ce dossier est interrogé par la commande `ctf-find`, une recherche **plein texte** (SQLite FTS5, classement BM25). Il n'y a **aucune IA ni recherche sémantique** : la recherche ne trouve que les mots réellement écrits dans les fichiers. Toutes les règles ci-dessous en découlent : un write-up est retrouvable uniquement si les mots qu'on taperait pour le chercher y figurent, de préférence dans les champs les mieux pondérés.

## Comment `ctf-find` fonctionne (à connaître avant d'écrire)

- **Fichiers pris en compte** : uniquement ceux nommés `writeup.md`, à l'emplacement exact `<CTF>/CHALLENGES/<Catégorie>/<Challenge>/writeup.md`. Le CTF, la catégorie et le nom du challenge sont déduits du chemin (1er, 3e et 4e niveau). Toute imbrication supplémentaire fausse cette identification : ne jamais ajouter de sous-dossier entre le challenge et `writeup.md`.
- **Champs indexés et poids de pertinence** (du plus fort au plus faible) :
  1. `techniques` (poids 8)
  2. `keywords` (poids 6)
  3. nom du challenge + `title` (poids 6)
  4. `tools` (poids 2)
  5. CTF, catégorie, et tout le texte du corps (poids 1)
  Les autres champs du frontmatter (`difficulty`, `points`, `status`, `has_script`, `source`...) ne sont pas indexés : ils servent à l'information.
- **Découpage des mots** : tout caractère non alphanumérique sépare les mots. `ntds.dit` devient `ntds` et `dit` ; `rsa-small-exponent` devient `rsa`, `small`, `exponent`. La casse et les accents sont ignorés. Les mots de la requête sont cherchés comme préfixes (`overflow` trouve `overflows`).
- **Logique de requête** : tous les mots tapés doivent apparaître dans le même write-up. Si aucun write-up ne les contient tous, la recherche s'élargit à l'un OU l'autre.
- **Pas de synonymes, pas de traduction** : `dépassement de tampon` ne trouvera pas un write-up qui ne contient que `buffer overflow`. Il faut donc écrire **les deux langues et les variantes** dans `keywords`.
- **Résultat affiché** : CTF › catégorie › challenge, techniques, extrait d'environ 14 mots autour de la correspondance, chemin du fichier.

## Arborescence (à respecter toujours)

~~~
CTFs-Write-ups-Database/
├── CLAUDE.md
├── INDEX.md
├── TAXONOMY.md
└── <CTF>/
    └── CHALLENGES/
        └── <Catégorie>/
            └── <Challenge>/
                ├── writeup.md
                └── scripts/      (uniquement s'il existe des scripts de solve)
~~~

- Les noms de CTF, de catégorie et de challenge reprennent exactement ceux du dossier source.
- Le fichier s'appelle toujours `writeup.md` (jamais note.md ni notes.md).
- Les fichiers fournis par le challenge (binaires, images, dumps, archives) ne sont PAS copiés : on les mentionne dans le write-up (nom, type).

## Règles d'écriture pour la recherche plein texte

1. **Le champ `keywords` est le plus important.** 8 à 15 entrées, en minuscules, sur **une seule ligne**, qui mélangent :
   - français et anglais (`dépassement de tampon, buffer overflow`) ;
   - le nom de l'attaque ou de la vulnérabilité et ses variantes (`sqli, sql injection, injection sql`) ;
   - les noms exacts des outils (`secretsdump, impacket, volatility`) ;
   - les formats et extensions (`ntds.dit, pcap, elf, pyc, kdbx`) ;
   - les protocoles et services (`kerberos, ldap, smb`) ;
   - les fonctions, bibliothèques ou identifiants remarquables (`gets, strcpy, ret2libc, cve-2021-3156`) ;
   - les symptômes ou messages d'erreur caractéristiques, tels qu'on les tapera pour chercher.
2. **`techniques`** : 1 à 4 valeurs normalisées en kebab-case, prises dans `TAXONOMY.md` (voir plus bas). Comme `-` sépare les mots, `rsa-small-exponent` est retrouvé par `rsa small` ou `exponent`.
3. **Écrire les termes littéralement dans le corps.** La première phrase du "Résumé" nomme la catégorie et la technique principale. Chaque entrée de "Signaux de reconnaissance" contient les mots précis (valeurs, noms de fonctions, extensions, messages) plutôt qu'une description vague.
4. **Un write-up = un challenge.** Ne pas mélanger plusieurs challenges dans un fichier, sinon le classement devient imprécis.
5. **Langue** : English.

The write-up text must be in English. Technical terms, commands, and tool names must be in English (as they already are). The English must be easy to comprehend and follow. French text is only accepted in the "Non renseigné" fields when no equivalent exists.
6. **Aucune information inventée.** Valeur manquante : `Non renseigné` (et `keywords` limité à ce qui est réellement connu).
7. Toujours donner le "pourquoi" du déclenchement : quel signal a mis sur la piste. C'est la section qu'on cherche le plus souvent ("quand penser à X").

## Format du frontmatter (strict, lu par un parseur simple)

- La toute première ligne du fichier est `---`, et le bloc se termine par une ligne `---`.
- Une clé par ligne, au format `clé: valeur`.
- Les listes tiennent sur **une seule ligne** entre crochets : `techniques: [rsa-small-exponent, cube-root]`.
- Pas de listes à tirets, pas de valeurs sur plusieurs lignes, pas de commentaires.

## Modèle de write-up (`writeup.md`)

~~~markdown
---
title: "<Nom du challenge>"
ctf: "<Nom du CTF>"
category: "<crypto | pwn | forensics | web | reverse | misc | osint | stego | ...>"
difficulty: "<easy | medium | hard | Non renseigné>"
points: <nombre ou null>
techniques: [<technique-1>, <technique-2>]
tools: [<outil-1>, <outil-2>]
keywords: [<mot-clé fr>, <mot-clé en>, <extension>, <outil>, <variante>, ...]
status: "<solved | partial>"
has_script: <true | false>
source: "<chemin relatif du fichier de notes d'origine>"
---

# <Nom du challenge> (<CTF>, <catégorie>)

## Résumé
2 à 3 phrases : ce qu'est le challenge, la catégorie, la technique clé utilisée, le résultat. Reprendre ici les termes principaux (technique, outil, format).

## Énoncé et artefacts
Énoncé résumé. Liste des fichiers ou services fournis (nom, type, version si pertinente : glibc, Python, etc.).

## Signaux de reconnaissance
Liste à puces des indices qui ont mis sur la piste (valeurs particulières, comportement observé, format du fichier, protection du binaire, message d'erreur...). Forme : "Si on observe X, penser à Y", avec X et Y en mots précis.

## Méthode de résolution
Étapes numérotées, chacune avec l'action, la commande ou le code utile, et le résultat attendu.

## Pistes écartées
Ce qui a été essayé sans succès et pourquoi. Section omise si les notes n'en parlent pas.

## Script de solve
Chemin du script : `scripts/<nom>`. Section omise si aucun script de solve n'est présent.

## Flag
`<flag>` ou `Non renseigné`.

## Leçons et patterns réutilisables
2 à 5 puces : ce qu'il faut retenir pour reconnaître et résoudre un challenge similaire.
~~~

## TAXONOMY.md
Liste unique et à jour des valeurs utilisées pour `techniques`, `tools` et `category`, groupées par catégorie. Avant d'utiliser une nouvelle valeur, vérifier si une équivalente existe déjà et la réutiliser (par exemple `heap-use-after-free` et jamais `uaf-heap` ailleurs). Format kebab-case en minuscules. Ce fichier n'est pas indexé par `ctf-find` : il sert à garder un vocabulaire cohérent.

## INDEX.md
Un tableau par CTF avec les colonnes : Catégorie | Challenge | Techniques | Script (oui/non) | Chemin du writeup.md. Fichier de lecture pour l'humain, non indexé.

## Scripts de solve
- Copier les scripts dans `<Challenge>/scripts/` en gardant leur nom d'origine.
- Sont des scripts : `.py`, `.sage`, `.sh`, `.c`, `.cpp`, `.js`, `.rb`, `.go`, `.rs`, `.pl`, `.php`, ainsi que les fichiers nommés solve*, exploit*, decrypt*, brute*, payload*, gen*.
- Ne pas copier les fichiers fournis par le challenge, les gros fichiers (plus de 1 Mo), ni les binaires.
- Ajouter en tête du script copié un commentaire d'une ligne indiquant le challenge, uniquement si le fichier n'en a pas déjà un.

## Root-Me : API, secrets et fichiers fournis

- La configuration Root-Me (clé API + session web SPIP) est stockée **hors du dépôt**, dans `/workspace/Root-Me/config.sh`. La lire uniquement depuis ce fichier ; ne jamais la recopier dans un write-up, un script versionné ou une réponse.
- Pour récupérer un énoncé officiel, utiliser la page anglaise du challenge. Les pages HTML sont protégées par Anubis : prévoir un navigateur ou un client qui résout le proof-of-work.
- Ne pas télécharger les archives uniquement pour décrire leur contenu : référencer le fichier tel qu'il apparaît sur la plateforme, avec son lien direct.

## Contrôle avant de terminer un write-up

- Le chemin respecte `<CTF>/CHALLENGES/<Catégorie>/<Challenge>/writeup.md`.
- Le frontmatter respecte le format strict ci-dessus.
- `keywords` contient 8 à 15 entrées, avec les variantes françaises et anglaises.
- `techniques` ne contient que des valeurs présentes dans `TAXONOMY.md` (à ajouter sinon).
- Le "Résumé" nomme la catégorie et la technique principale.
- Test final : lancer `ctf-find` avec 2 ou 3 mots que l'on taperait pour retrouver ce challenge et vérifier qu'il apparaît dans les premiers résultats.