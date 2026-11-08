---
title: "Kerberos-Authentication"
ctf: "Root-Me"
category: "network"
difficulty: "Not specified"
points: null
techniques: ["password-cracking", "pcap-analysis", "kerberos", "encoding", "hash-cracking"]
tools: ["tshark", "john"]
keywords: ["Kerberos-Authentication", "Root-Me", "network", "password-cracking", "pcap-analysis", "kerberos", "encoding", "hash-cracking", "tshark", "john", "pcapng", "aes"]
status: "solved"
has_script: false
source: "Root-Me/Network/Kerberos-Authentication/solve.md"
---

# Kerberos-Authentication (Root-Me, network)

## Summary
Challenge **Kerberos-Authentication** from the Root-Me CTF, network category. Main technique: password-cracking. We convert the.pcapng to.pdml to be able to extract the hash and break it

## Statement and artefacts
We convert the.pcapng to.pdml to be able to extract the hash and break it

**Provided files / artifacts:**
- `CredentialDump-Session.log (text, 0 B)`
- `ch29.zip (archive, 9.5 KB)`
- `hash.txt (text, 154 B)`
- `kerberos_auth.pcapng (network capture, 21.0 KB)`
- `kerberos_auth.pdml (file, 1.9 MB)`

## Recognition signals
Not specified.

## Resolution method
1. We convert the.pcapng to.pdml to be able to extract the hash and break it

```bash
❯❯ tshark -r kerberos_auth.pcapng -Y 'kerberos'                                         
Running as user "root" and group "root". This could be dangerous.
   51 0.045193731 192.168.122.1 → 192.168.122.100 KRB5 247 AS-REQ
   52 0.045633481 192.168.122.100 → 192.168.122.1 KRB5 248 KRB Error: KRB5KDC_ERR_PREAUTH_REQUIRED
   60 0.199721071 192.168.122.1 → 192.168.122.100 KRB5 327 AS-REQ
   61 0.200506493 192.168.122.100 → 192.168.122.1 KRB5 1741 AS-REP
   69 0.204321887 192.168.122.1 → 192.168.122.100 KRB5 1626 TGS-REQ
   71 0.205044249 192.168.122.100 → 192.168.122.1 KRB5 1648 TGS-REP
   76 0.208290706 192.168.122.1 → 192.168.122.100 SMB2 1594 Session Setup Request

❯❯ tshark -r kerberos_auth.pcapng -T pdml > kerberos_auth.pdml
krb2john.py kerberos_auth.pdml
Running as user "root" and group "root". This could be dangerous.
[-] Hash might be broken, etype != 23 and salt not found!
william.dupond:$krb5pa$18$william.dupond$CATCORP.LOCAL$$fc8bbe22b2c967b222ed73dd7616ea71b2ae0c1b0c3688bfff7fecffdebd4054471350cb6e36d3b55ba3420
be6c0210b2d978d3f51d1eb4f
Currently unsupported etype 18 found!
Unable to find kerberos.salt value. Please report this bug to us!

❯❯ john hash.txt                    
Using default input encoding: UTF-8 
Loaded 1 password hash (krb5pa-sha1, Kerberos 5 AS-REQ Pre-Auth etype 17/18 [PBKDF2-SHA1 (AES-CTS-HMAC-SHA1-96)128/128 SSE2 4x])
Cost 1 (etype) is 18 for all loaded hashes
Will run 12 OpenMP threads
Proceeding with single, rules:Single
Press 'q' or Ctrl-C to abort, 'h' for help, almost any other key for status
Almost done: Processing the remaining buffered candidate passwords, if any.
Proceeding with wordlist:/opt/tools/john/run/password.lst
Enabling duplicate candidate password suppressor using 256 MiB
Failed to use huge pages (not pre-allocated via sysctl? that's fine)
kittycat12       (?)     
1g 0:00:00:02 DONE 2/3 (2026-11-04 17:16) 0.3861g/s 11861p/s 11861c/s 11861C/s diablo11..square1
Use the "--show" option to display all of the cracked passwords reliably
Session completed
```

## Flag
RM{william.dupond@catcorp.local:kittycat12}

## Lessons and reusable patterns
- Main technique: password-cracking.
