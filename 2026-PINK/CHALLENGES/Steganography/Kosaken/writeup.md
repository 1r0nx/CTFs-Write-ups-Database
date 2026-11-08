---
title: "Kosaken"
ctf: "2026-PINK"
category: "stego"
difficulty: "Not specified"
points: 50
techniques: []
tools: []
keywords: ["Kosaken", "PINK", "stego"]
status: "solved"
has_script: false
source: "PINK/CHALLENGES/Steganography/Kosaken/notes.md"
---

# Kosaken (PINK, stego)

## Summary
Challenge **Kosaken** from the PINK CTF, stego category. Kosaken.txt is a full emoji transcription of the lyrics to “Moskau” by Dschinghis Khan (1979). The title of the challenge, Kosaken, is precisely a word from the chorus. The text contains stray emojis inserted into the lyrics.

## Statement and artefacts
I feel like something doesn't belong here...

**Provided files / artifacts:**
- `work/Kosaken.txt (text, 1.6 KB)`

## Recognition signals
- Signal: The emoji stanzas match the lyrics.
- Signal: | Emojis | Lyrics | |---|---| | 🏰🍻 | Moskau, Moskau | | 🥂➡️🧱💥 | wirf die Gläser an die Wand | | 🇷🇺😍🌍 | Russland ist ein schönes Land | | 🎉🎉🎉🎉🎉🙌 | ho-ho-ho-ho-ho, hey | | ❤️‍🔥🌌♾️ | deine Seele ist so big | | 🌙😈🎉 | nachts, da ist der Teufel los | | ❤️👅🥚🐟✨ | Liebe schmeckt wie Kaviar | | 👧💋❤️ | Mädchen sind zum Küssen da | | 🕺💃🪑➡️🪵💥 | komm, wir tanzen auf dem Tisch | | 🍾🥃❄️ | Wodka trinkt man pur und kalt | | 👴🏻🥂🚫 | Väterchen, dein Glas ist leer | | 🏚️⬇️🍾🍾🍾 | doch im Keller ist noch mehr |.
- Signal: The line “Kosaken, hey, hey, hey, leert die Gläser” is present in the stanzas 🧔🏻‍♂️🥂🙌 / 🙌🙌 / 👩🏻🌸😍 / 😄😄 ….

## Resolution method
1. **Spot intruders**

In each verse, one or more emojis do not match any words in the lyrics. The first ones already give the prefix:

| Line | Emoji | English name | Letter |
|---|---|---|---|
| 4 | 🍕 | pizza | **P** |
| 16 | 🇮🇹 | Italy | **I** |
| 20 | 👃 | nose | **N** |
| 25 | 🔑 | key | **K** |

Then the complete sequence:

| Line | Emoji | English name | Letter |
|---|---|---|---|
| 31 | 🫲 | left hand | L |
| 40 | 🐘 | elephant | E |
| 48 | 🦅 | eagle | E |
| 53 | 🌈 | rainbow | R |
| 56 | 🐯 | tiger | T |
| 66 | 🐶 | dog | D |
| 69 | ℹ️ | information | I |
| 75 | ✉️ | envelope | E |
| 82 | 🍇 | grapes | G |
| 84 | 🦁 | lion | L |
| 87 | 🍎 | apple | A |
| 89 | 🌲 | evergreen tree | E |
| 93 | 🐍 | snake | S |
| 98 | 👀 | eyes | E |
| 102 | 🐇 | rabbit | R |

2. **Message**

```
PINK LEERT DIE GLAESER
```

→ `PINK{LEERT_DIE_GLAESER}`.

3. **Notes**

- Odd emojis are often placed at the end of a line (`🏰🍻🐯`, `🏰🍻🍎`, `🇷🇺😍🌍🌲`, `🏰🍻🍇`, `🏰🍻✉️`, `🏰🍻🐇`) or at the beginning of a line (`🐍❤️‍🔥…`), making them easy to spot.
- A few additional emojis are **not** part of the message: `➖` (line 63), `🫱` (line 103), `😮` (lines 72–73). They serve as legitimate/decoy representations for “los”, “bis/zusammen” and “oh”.
- The transcription uses the common English names of emojis (`pizza`, `Italy`, `nose`, `key`, `apple`, `evergreen tree`…), not the full Unicode names (which would result in e.g. `RED APPLE` → R).
- The correct German word is *Gläser*; `AE` is the standard ASCII transliteration of `Ä`. This is why the sequence contains `A` then `E`.

4. **Recognize the song**

The emoji stanzas correspond to the lyrics:

| Emojis | Lyrics |
|---|---|
| `🏰🍻` | Moskau, Moskau |
| `🥂➡️🧱💥` | wirf die Gläser an die Wand |
| `🇷🇺😍🌍` | Russland ist ein schönes Land |
| `🎉🎉🎉🎉🎉🙌` | ho-ho-ho-ho-ho, hey |
| `❤️‍🔥🌌♾️` | deine Seele ist so groß |
| `🌙😈🎉` | nachts, da ist der Teufel los |
| `❤️👅🥚🐟✨` | Liebe schmeckt wie Kaviar |
| `👧💋❤️` | Mädchen sind zum Küssen da |
| `🕺💃🪑➡️🪵💥` | komm, wir tanzen auf dem Tisch |
| `🍾🥃❄️` | Wodka trinkt man pur und kalt |
| `👴🏻🥂🚫` | Väterchen, dein Glas ist leer |
| `🏚️⬇️🍾🍾🍾` | doch im Keller ist noch mehr |

The line “Kosaken, hey, hey, hey, leert die Gläser” is present in the stanzas `🧔🏻‍♂️🥂🙌 / 🙌🙌 / 👩🏻🌸😍 / 😄😄 …`.

## Flag
PINK{LEERT_DIE_GLAESER}

## Lessons and reusable patterns
Not specified.
