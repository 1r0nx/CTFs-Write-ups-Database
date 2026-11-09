---
title: "Secure Admin"
ctf: "2025-SADC-NextGenCyber-CTF"
category: "Boot2root"
difficulty: "Not specified"
points: 0
techniques: ["reverse"]
tools: []
keywords: ["admin", "boot2root", "secure"]
status: "solved"
has_script: false
source: "2025-SADC-NextGenCyber-CTF/Boot2root/Secure-Admin/writeup.md"
---

## Summary

Challenge **Secure Admin** from the 2025-SADC-NextGenCyber-CTF CTF, boot2root category.

## Statement and artefacts

See the original challenge files and images in this directory.

## Recognition signals

- (see resolution method below)

## Resolution method

# Secure Admin

![Screenshot From 2025-11-09 09-27-10.png](img/Screenshot_From_2025-11-09_09-27-10.png)

I did an ennumeration of the url

![1.png](img/1.png)

Here is the content of the robots.txt

![2.png](img/2.png)

When I tried to access the /flag.html I got rick rolled

This is the content of the .htaccess

![3.png](img/3.png)

We got what looks like a endpoitnt for an Local File Inclusion

When trying to access the endpoint here is the result

![3_1.png](img/3_1.png)

This looks like an Local File Inclusion

By trying numerous logs file, the path “/var/log/auth.log” displayed the log files of the ssh server

![3_2.png](img/3_2.png)

Now that we can read the ssh log file I tried a ssh log poisoning attack

![7.png](img/7.png)

I used metasploit to poison the log file by setting the username on a php payload

![8.png](img/8.png)

![9.png](img/9.png)

Now I can execute commands on the server.

I run all sort of commands accross the server to try to find the flag but nothing.

From here this is the work of ones of my team members: [D4rkC4rl](https://github.com/Fabrice000) 

He tried to list all SUID files capabilities and he found that the “gawk” SUID is set

![Screenshot From 2025-11-07 12-54-08.png](img/Screenshot_From_2025-11-07_12-54-08.png)

He got a reverse shell over the network with ngrok and he used the SUID to read the file in “/root/flag.txt”

**FLAG:** SADC{SSH_Poisoning!_D4rkN3t@W1zard}

## Flag

SADC{SSH_Poisoning!_D4rkN3t@W1zard}

## Lessons and reusable patterns

- (see resolution method above)
