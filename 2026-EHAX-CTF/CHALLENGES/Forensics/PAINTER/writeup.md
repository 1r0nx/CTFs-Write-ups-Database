---
title: "PAINTER"
ctf: "2026-EHAX-CTF"
category: "Forensics"
difficulty: "Not specified"
points: 0
techniques: ["forensics"]
tools: ["python", "tshark", "wireshark"]
keywords: ["forensics", "painter"]
status: "solved"
has_script: false
source: "2026-EHAX-CTF/Forensics/PAINTER/writeup.md"
---

## Summary

Challenge **PAINTER** from the 2026-EHAX-CTF CTF, forensics category.

## Statement and artefacts

See the original challenge files and images in this directory.

## Recognition signals

- (see resolution method below)

## Resolution method

# PAINTER

![Screenshot From 2026-03-01 09-42-00.png](img/Screenshot_From_2026-03-01_09-42-00.png)

For this challenge is given a .pcap file.

Opening it in wireshark show that it’s a capture of USB protocol

![image.png](img/image.png)

Now by looking around google and AI help I found something called “7-byte mouse report”

![image.png](img/image_1.png)

First I extracted the mouses data with:

```python
tshark -r pref.pcap -T fields -e usb.capdata > data.txt
```

Here is an overview of the file:

![image.png](img/image_2.png)

And wrote a python script to recover the mouse path 

[solve.py](scripts/solve.py)

That gave this image:

![Figure_2.png](img/Figure_2.png)

**FLAG:** EH4X{wh4t_c0l0ur_15_th3_fl4g}

## Flag

EH4X{wh4t_c0l0ur_15_th3_fl4g}

## Lessons and reusable patterns

- (see resolution method above)
