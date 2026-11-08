---
title: "Sheldon Treasure Trail"
ctf: "2025_SADC-NextGenCyber-CTF"
category: "Boot2root"
difficulty: "Not specified"
points: 0
techniques: ["rfi", "web"]
tools: []
keywords: ["boot2root", "sheldon", "trail", "treasure"]
status: "solved"
has_script: false
source: "2025_SADC-NextGenCyber-CTF/Boot2root/Sheldon-Treasure-Trail/writeup.md"
---

## Summary

Challenge **Sheldon Treasure Trail** from the 2025_SADC-NextGenCyber-CTF CTF, boot2root category.

## Statement and artefacts

See the original challenge files and images in this directory.

## Recognition signals

- (see resolution method below)

## Resolution method

# Sheldon Treasure Trail

![Screenshot From 2025-11-09 09-27-57.png](img/Screenshot_From_2025-11-09_09-27-57.png)

The display of the url

![Screenshot From 2025-11-06 19-54-34.png](img/Screenshot_From_2025-11-06_19-54-34.png)

Let’s do some ennumeration with gobuster

![Screenshot From 2025-11-06 19-53-33.png](img/Screenshot_From_2025-11-06_19-53-33.png)

I went to the /fetch and supply “google.com” as url

![Screenshot From 2025-11-06 19-55-34.png](img/Screenshot_From_2025-11-06_19-55-34.png)

I got some errors and by reading I found an interesting url “http://admin_api:9008”

I supply the url I found as the fetch parameter and got this. 

![Screenshot From 2025-11-06 19-56-11.png](img/Screenshot_From_2025-11-06_19-56-11.png)

It says that the real endpoint is not far…

I went to burpsuite and found another interesting url

![Screenshot From 2025-11-06 19-57-00.png](img/Screenshot_From_2025-11-06_19-57-00.png)

I opened the url and a got a lot of things. But here is the interesting path “/render”

![Screenshot From 2025-11-06 19-57-29.png](img/Screenshot_From_2025-11-06_19-57-29.png)

I’ve then substitute the “/admin” by “/render” and got this

![Screenshot From 2025-11-06 19-58-21.png](img/Screenshot_From_2025-11-06_19-58-21.png)

I can write a custom template and run it.This looks like Server Side Template Injection vulnerability

![Screenshot From 2025-11-06 19-58-46.png](img/Screenshot_From_2025-11-06_19-58-46.png)

By searching for the vulnerabilty on the web I found a payload to use

![Screenshot From 2025-11-06 20-11-58.png](img/Screenshot_From_2025-11-06_20-11-58.png)

![Screenshot From 2025-11-06 19-59-41.png](img/Screenshot_From_2025-11-06_19-59-41.png)

Here is the result. And now I can sucessfully execute commands on the server

![Screenshot From 2025-11-06 19-59-54.png](img/Screenshot_From_2025-11-06_19-59-54.png)

I tried to read the flag and this is the result 

![Screenshot From 2025-11-06 20-00-28.png](img/Screenshot_From_2025-11-06_20-00-28.png)

Looks like we’re not done yet

By looking almost everywhere on the server I found a Dockerfile under a user under /home  directory

![Screenshot From 2025-11-06 20-04-35.png](img/Screenshot_From_2025-11-06_20-04-35.png)

![Screenshot From 2025-11-06 20-05-03.png](img/Screenshot_From_2025-11-06_20-05-03.png)

**FLAG:** SADC{chained_exploit_ssrf_ssti_rce_lpe}

## Flag

SADC{chained_exploit_ssrf_ssti_rce_lpe}

## Lessons and reusable patterns

- (see resolution method above)
