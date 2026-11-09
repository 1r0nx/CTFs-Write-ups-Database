---
title: "PAD-PAD-PAD"
ctf: "Pwny-CTF"
category: "crypto"
difficulty: "Not specified"
points: 350
techniques: ["xor-cipher", "encoding", "malware-analysis"]
tools: ["python"]
keywords: ["PAD-PAD-PAD", "Pwny-CTF", "crypto", "xor-cipher", "encoding", "malware-analysis", "python", "xor", "hex"]
status: "solved"
has_script: true
source: "Pwny-CTF/CHALLENGES/Crypto-I/PAD-PAD-PAD/notes.md"
---

# PAD-PAD-PAD (Pwny-CTF, crypto)

## Summary
Challenge **PAD-PAD-PAD** from the Pwny-CTF CTF, crypto category. Main technique: xor-cipher. NEVER reuse a one-time pad. Two encrypted under the same key -> c1⊕c2 = m1⊕m2, and with

## Statement and artefacts
You've acquired multiple ciphertexts that have been XORd with the same one-time pad.

Can you perform some cryptanalysis and decrypt the flag given the encrypted output in "message.txt"?

11 messages are XORed with **the same** random key (`os.urandom(1024)`). `message.txt` is the list of ciphers (hex). Find the flag. Hint: “an OTP is only secure if it is used once”.

**Provided files / artifacts:**
- `work/message.txt (text, 2.5 KB)`

## Recognition signals
Not specified.

## Resolution method
1. **The reasoning**

One-time pad = `c = m ⊕ key`. Unbreakable **if** `key` is random, as long as `m`, and used **once**. Here the **same** key number 11 messages → **many-time pad**.

Key reused ⇒ for two messages: `c_i ⊕ c_j = m_i ⊕ m_j` (the key disappears). As the plaintexts are **English**, we exploit the structure. Two equivalent techniques:
- **Space attack**: the space byte `0x20` XORed with a letter gives the same letter in reverse case. In a column, spotting which message has a space reveals the key for that column.
- **Scoring by column** (used here): for each column `j`, try the 256 values of `key[j]` and keep the one that makes all `m_i[j]` printable and "the most English" (spaces/weighted lowercase). We thus recover the key column by column, then we decrypt everything.

**Sparsely covered** columns (few messages of this length) come out noisy. We correct them with the **crib** `sigpwny{` at the top of the flag message and the **context** (“they rebooted mtv **cribs** in 2021” — MTV Cribs was relaunched in 2021). The key thus deduced decrypts **all** the other messages in perfect English ("Crib dragging is a known plain text attack..."), which **validates**:
```
```

## Solve script
Script path: [scripts/solve.py](scripts/solve.py)

## Flag
sigpwny{they_rebooted_mtv_cribs_in_2021}

## Lessons and reusable patterns
- NEVER reuse a one-time pad. Two encrypted under the same key -> c1⊕c2 = m1⊕m2, and with
- Crib-dragging: drag a probable word (sigpwny{, "the", "and"...) along the c_i⊕c_j
- The more messages there are per column, the more reliable the recovery; rare columns end
- Script: work/solve.py.
