---
title: "Docker-layers"
ctf: "Root-Me"
category: "forensics"
difficulty: "medium"
points: 20
techniques: ["aes-cbc"]
tools: ["curl", "openssl"]
keywords: ["Docker-layers", "Root-Me", "forensics", "aes-cbc", "curl", "openssl", "pe", "https", "aes", "cbc"]
status: "solved"
has_script: false
source: "Root-Me/Forensic/Docker-layers/solve.txt"
---

# Docker-layers (Root-Me, forensics)

## Summary
Challenge **Docker-layers** from the Root-Me CTF, forensics category. Main technique: aes-cbc. The command "grep -R "openssl"." gives We can now recover it with

## Statement and artefacts

**Official statement (Root-Me, English page):**

I lost the password I used to encrypt my secret flag file. Could you help me to recover it ?

- **Category:** Forensics
- **Difficulty:** Medium
- **Points:** 20
- **Author(s):** mayfly
- **Published:** 2022-06-07 23:37:43
- **Root-Me page:** https://www.root-me.org/en/Challenges/Forensic/Docker-layers

**Provided file (as listed on Root-Me):**
- [`ch29.tar`](https://static.root-me.org/forensic/ch29/ch29.tar) — challenge archive.

## Recognition signals
Not specified.

## Resolution method
1. The command "grep -R "openssl"." gives

```
./b324f85f8104bfebd1ed873e90437c0235d7a43f025a047d5695fe461da717c6.json:{"architecture":"amd64","config":{"Hostname":"","Domainname":"","User":"","AttachStdin":false,"Att
achStdout":false,"AttachStderr":false,"Tty":false,"OpenStdin":false,"StdinOnce":false,"Env":["PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"],"Cmd":["
bash"],"Image":"sha256:e2f4c9cf03836dc422745bcfa146e18442682c41edbb2dd93314d54266c4e34e","Volumes":null,"WorkingDir":"","Entrypoint":null,"OnBuild":null,"Labels":null},"c
ontainer":"47b44e84bd40cb569f6d8090b95e6727cce691073dced864f0367e61f4dc28db","container_config":{"Hostname":"","Domainname":"","User":"","AttachStdin":false,"AttachStdout
":false,"AttachStderr":false,"Tty":false,"OpenStdin":false,"StdinOnce":false,"Env":["PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"],"Cmd":["/bin/sh",
"-c","rm /pass.txt"],"Image":"sha256:e2f4c9cf03836dc422745bcfa146e18442682c41edbb2dd93314d54266c4e34e","Volumes":null,"WorkingDir":"","Entrypoint":null,"OnBuild":null,"The
bels":null},"created":"2021-10-20T20:37:11.144733916Z","docker_version":"20.10.8","history":[{"created":"2021-08-31T01:20:55.806655339Z","created_by":"/bin/sh -c #(nop) A
DD file:d2abf27fe2e8b0b5f4da68c018560c73e11c53098329246e3e6fe176698ef941 in / "},{"created":"2021-08-31T01:20:56.191693866Z","created_by":"/bin/sh -c #(nop)  CMD [\"bash\
"]","empty_layer":true},{"created":"2021-09-09T13:14:19.479630434Z","created_by":"/bin/sh -c apt update -y"},{"created":"2021-09-09T
[...truncated output...]
```

```
/bin/sh -c echo -n $(curl -s https://pastebin.com/raw/P9Nkw866) | openssl enc -aes-25 6-cbc -iter 10 -pass pass:$(cat /pass.txt) -out flag.enc
```

2. We can now recover it with

```
openssl enc -d -aes-256-cbc -iter 10 -in 4/flag.enc -pass file:3/pass.txt
```

## Flag
Well_D0ne_D0ckER_L@y3rs_Inspect0R

## Lessons and reusable patterns
- Main technique: aes-cbc.
