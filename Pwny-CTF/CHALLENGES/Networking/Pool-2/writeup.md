---
title: "Pool-2"
ctf: "Pwny-CTF"
category: "network"
difficulty: "hard"
points: null
techniques: ["password-cracking", "pcap-analysis", "ntlm", "smb", "encoding", "hash-cracking"]
tools: ["tshark", "john", "hashcat"]
keywords: ["Pool-2", "Pwny-CTF", "network", "password-cracking", "pcap-analysis", "ntlm", "smb", "encoding", "hash-cracking", "tshark", "john", "hashcat", "pcap", "tcp", "hex"]
status: "solved"
has_script: false
source: "Pwny-CTF/CHALLENGES/Networking/Pool-2/notes.md"
---

# Pool-2 (Pwny-CTF, network)

## Summary
Challenge **Pool-2** from the Pwny-CTF CTF, network category. Main technique: password-cracking. NTLMv2 is a challenge-response: each login attempt (even a failed one) produces an independently crackable hash. Always crack the one for the successful attempt.

## Statement and artefacts
**Provided files / artifacts:**
- `CredentialDump-Session.log (text, 912.7 KB)`
- `hash (file, 647 B)`
- `info.txt (text, 2.2 KB)`
- `pool.pcap (network capture, 9.5 MB)`
- `work/all.pot (file, 0 B)`
- `work/all_hashes.txt (text, 825.2 KB)`
- `work/hash_success.txt (text, 632 B)`
- `work/sample.pot (file, 0 B)`
- `work/sample25.txt (text, 15.4 KB)`

## Recognition signals
Not specified.

## Resolution method
1. **Locate account/hash** — `pcredz -f pool.pcap` (or manual extraction) outputs an **NTLMv2** hash for `Administrator`.
2. **Trap**: cracking a hash at random gives a **tried** password, not necessarily the right one. Here a first extraction gave `427730773` → **refused** (this was one of 1336 failed attempts).
3. **Count attempts** — `tshark -r pool.pcap -Y 'smb2.cmd==1 && smb2.flags.response==1' -T fields -e smb2.nt_status | sort | uniq -c`:
   - `0xc0000016` MORE_PROCESSING_REQUIRED (normal step), `0xc000006d` LOGON_FAILURE, `0xc0000022` ACCESS_DENIED (chess),
   - **`0x00000000` SUCCESS = 1 only** → the correct attempt.
4. **Isolate successful connection** — recover its `tcp.stream`: `... && smb2.nt_status==0x00000000 -T fields -e tcp.stream`.
5. **Extract the 4 pieces of the NTLMv2 hash** in this stream:
   - server challenge (NTLMSSP message **type 2**): `ntlmssp.ntlmserverchallenge` → `b2e621d7d5b6c51c`
   - username/domain/NTProofStr/response (message **type 3**): `ntlmssp.auth.username`, `ntlmssp.auth.domain`, `ntlmssp.ntlmv2_response.ntproofstr`, `ntlmssp.ntlmv2_response`.
6. **Rebuild in john format**: `user::domain:ServerChallenge:NTProofStr:blob` where `blob` = the NTLMv2 response **without its first 32 hexes** (the NTProofStr).
7. **Cracker** — `john --format=netntlmv2 hash --wordlist=rockyou.txt` → `dontcountonit`.
8. Flag = `sigpwny{dontcountonit}`.

1. **More difficult variation**

- Password **excluding rockyou** → rules (`--rules`) or mask (`hashcat -a 3`).
- Multiple accounts / multiple successes → crack each hash and cross-check with the targeted account.
- SMB traffic **encrypted** (SMB3 encryption) → the challenge-response is no longer readable in plain text.

## Flag
sigpwny{dontcountonit}

## Lessons and reusable patterns
- NTLMv2 is a challenge-response: each login attempt (even a failed one) produces an independently crackable hash. Always crack the one for the successful attempt.
- Useful SMB2 status codes: 0x00000000 SUCCESS, 0xc0000016 MORE_PROCESSING_REQUIRED (normal, not a failure), 0xc000006d LOGON_FAILURE, 0xc0000022 ACCESS_DENIED.
- john/hashcat NTLMv2 format (hashcat 5600 mode): user::domain:ServerChallenge:NTProofStr:blob.
- ServerChallenge = NTLMSSP type 2 message (8 bytes).
- ntlmssp.ntlmv2_response = NTProofStr (16 B) + blob -> separate both by:.
- Classic error: put the NTProofStr instead of the ServerChallenge, or forget it: -> john loads the hash as a simple NT and finds nothing.
