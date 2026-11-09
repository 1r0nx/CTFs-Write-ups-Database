---
title: "Archive"
ctf: "2025-SADC-NextGenCyber-CTF"
category: "Forensics"
difficulty: "Not specified"
points: 0
techniques: ["forensics", "web"]
tools: ["unzip"]
keywords: ["archive", "forensics"]
status: "solved"
has_script: false
source: "2025-SADC-NextGenCyber-CTF/Forensics/Archive/writeup.md"
---

## Summary

Challenge **Archive** from the 2025-SADC-NextGenCyber-CTF CTF, forensics category.

## Statement and artefacts

See the original challenge files and images in this directory.

## Recognition signals

- (see resolution method below)

## Resolution method

# Archive

![Screenshot From 2025-11-09 09-36-52.png](img/Screenshot_From_2025-11-09_09-36-52.png)

The content of the file looks like base64 and trying to decode it in the terminal doesnt give anything readable. I used a website to convert base64 content into a file

![1.png](img/1.png)

With the file downloaded, trying to unzip gives us this

![2.png](img/2.png)

The output says that the file have been ziped 499 times. So I used a loop to unzip it 

![3.png](img/3.png)

![4.png](img/4.png)

We can see now that the file have been archived 499 times.

 Loop again!!!

![5.png](img/5.png)

![6.png](img/6.png)

**FLAG:** SADC{th3_qu357_15_c0mpl3t3d_3njoy_your_g1f7_buddy}

## Flag

SADC{th3_qu357_15_c0mpl3t3d_3njoy_your_g1f7_buddy}

## Lessons and reusable patterns

- (see resolution method above)
