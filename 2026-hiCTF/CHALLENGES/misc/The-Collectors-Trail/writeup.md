---
title: "The-Collectors-Trail"
ctf: "2026-hiCTF"
category: "misc"
difficulty: "Not specified"
points: null
techniques: ["disk-forensics", "osint", "git-forensics", "encoding"]
tools: ["strings", "binwalk", "steghide", "zsteg", "unzip", "7z", "git"]
keywords: ["The-Collectors-Trail", "hiCTF", "misc", "disk-forensics", "osint", "git-forensics", "encoding", "strings", "binwalk", "steghide", "zsteg", "unzip", "7z", "git", "zip", "png"]
status: "solved"
has_script: false
source: "hiCTF/misc/The-Collectors-Trail/notes.md"
---

# The-Collectors-Trail (hiCTF, misc)

## Summary
Challenge **The-Collectors-Trail** from the hiCTF CTF, misc category. Main technique: disk-forensics. Six different hiding techniques in images (one per work), exact official inventory numbers (OSINT) and a chain from HKDF -> zip AES -> LSB to positions pulled by HMAC -> Release GitHub -> AES-GCM.

## Statement and artefacts
**Provided files / artifacts:**
- `the-collectors-trail.zip (archive, 36.0 MB)`

## Recognition signals
- Signal: six different hiding techniques in images (one per work), exact official inventory numbers (OSINT) and a chain of HKDF -> zip AES -> LSB to positions pulled by HMAC -> Release GitHub -> AES-GCM.
- Signal: Main trap: the inventory number. With belvedere.at/4494 for Schiele, 7z responded “Wrong password”. The correct one is Inv. 3171. Accession must always be verified on the official registry, and the slightest difference changes the SHA-256. The zip serves as an oracle here: we can test each hypothesis with 7z t.
- Signal: To recognize this type of challenge: several images, each with a clue. You must apply a technique per image, guided by the index, and not launch zsteg/binwalk randomly. Checksums allow you to know immediately that a fragment is good.
- Signal: The index “the serial is in the tag's note” designates the message of the annotated tag, not the description of the Release (which only contains “The catalog is complete.”).

## Resolution method
1. **Archive.** `sha256sum` gives the same hash as the statement. `unzip -l` lists `image_vault.zip` (6 folders `record-xxxx/` with `image` and `conservation.txt`, plus `catalogue/colophon.txt`) and `sealed_cabinet.zip`. `zipinfo` displays “u099”: it is **AES zip**, so `unzip` is not enough, you need `7z`.
2. **Read `colophon.txt`.** It gives the whole recipe: format of a fragment `16 hex-4 hex`, seal = `SHA-256(8 bytes)[:2]`, sorting by year of birth of the artist, HKDF, canonical addresses `domain/accession`, Steghide passphrase = full address.
3. **Identify the works.** Thumbnail sheet with ImageMagick: `convert "img[0]" -resize 600x600` then `montage`. The “1918” in the statement designates Schiele.
4. **Extract the fragments**, each guided by its `conservation.txt`:

1. | Record | Work (artist, birth) | Hint | Technical / control | Fragment |
|---|---|---|---|---|
| 31c8 | *The Starry Night* (Van Gogh, 1853) | “what survives when opacity disappears?” » | Pixels at **alpha = 0** but RGB ≠ white: we crop the area and record its RGB without the alpha. The text appears. | `c1d322deee71edf2-cfb8` |
| 5a73 | *The Scream* (Munch, 1863) | “every seventh position…blue” | Blue channel LSB, pixels 0, 7, 14… (`px[::7,2] & 1`) | `7141415e3a146329-c2dc` |
| 7f2a | *The Girl with the Pearl Earring* (Vermeer, 1632) | “inside the object’s own structure” | `strings`: private PNG chunk `coLl` | `be5f329a4841bece-ee99` |
| b19d | *Tres de mayo* (Goya, 1746) | “beyond the final mark” | Data after `IEND`, in base64 | `b086be35786cac71-8ab3` |
| d604 | *The Kiss* (Klimt, 1862) | “an identity, not merely a number” | `steghid extract -sf image -p belvedere.at/912` | `07961017e80fb1e3-b14e` |
| e2f1 | *Death and the Maiden* (Schiele, 1890) | “what precedes the row’s pixel data” | **Filter byte** of each PNG line (1 → 0, 2 → 1), 176 lines = 22 bytes | `74718896e450c77c-e551` |

2. All 6 seals have been verified (`sha256(bytes.fromhex(h)).hexdigest()[:4] == check`).

5. **Canonical addresses (OSINT)**, in birth order:

```
   mauritshuis.nl/670
   museodelprado.es/P000749
   moma.org/472.1941
   belvedere.at/912
   nasjonalmuseet.no/NG.M.00939
   belvedere.at/3171
   ```

6. **Firm password.** `master = HKDF (concatenated fragments, salt="collector-v2:ossuary", info="master")`, then `HKDF(master, salt=SHA256(addresses), info="zip", 16)` in hex. Verification: `7z t -p<password>` no longer returns errors.
7. **`stego.png`** (instructions in `readme.txt`). `key = HKDF(master, salt=b"", info="stego")`. Each position = `HMAC(key, counter on 8 bytes big-endian)[:8] mod (L×H×3)`; we skip the duplicates and read the LSB. Frame: length (4 B) + data + CRC-32. The CRC is valid and the message refers to GitHub Release `broski-creator/velarium-ossuary-ledger-7f3c2a`, tag `v1.0`, file `flag.enc`.
8. **GitHub.** The `releases/tags/v1.0` API gives the file, whose SHA-256 corresponds to that announced. `git/refs/tags/v1.0` shows that the object is an **annotated tag**, and `git/tags/<sha>` gives its message with `Serial: 1ec5d6c0…`.
9. **Flag.** `flag_key = HKDF(master, salt=serial, info="flag")`, then AES-256-GCM (nonce 12 ‖ ct ‖ tag 16, AAD `collector-v2`). A valid GCM tag proves that the entire chain is correct.

## Flag
hiCTF{marble_sparrow_9eb44602eedb764aac082a3816b7d7cb}

## Lessons and reusable patterns
- Main pitfall: the inventory number. With belvedere.at/4494 for Schiele, 7z responded “Wrong password”. The correct one is Inv. 3171. Accession must always be verified on the official registry, and the slightest difference changes the SHA-256. The zip serves as an oracle here: we can test each hypothesis with 7z t.
- The form of the address (belvedere.at/912, without sammlung.) was confirmed by steghide before calculating the zip password.
- To recognize this type of challenge: several images, each with a clue. You must apply a technique per image, guided by the index, and not launch zsteg/binwalk randomly. Checksums allow you to know immediately that a fragment is good.
- PNG filter bytes: only the lines at the beginning carry data (values 1 and 2). You must stop as soon as a filter has another value (0, 3, 4).
- The subscript "the serial is in the tag's note" refers to the annotated tag message, not the Release description (which only contains "The catalog is complete.").
