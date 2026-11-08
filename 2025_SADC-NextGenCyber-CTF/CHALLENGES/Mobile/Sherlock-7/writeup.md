---
title: "Sherlock 7"
ctf: "2025_SADC-NextGenCyber-CTF"
category: "Mobile"
difficulty: "Not specified"
points: 0
techniques: ["web"]
tools: []
keywords: ["7", "mobile", "sherlock"]
status: "solved"
has_script: false
source: "2025_SADC-NextGenCyber-CTF/Mobile/Sherlock-7/writeup.md"
---

## Summary

Challenge **Sherlock 7** from the 2025_SADC-NextGenCyber-CTF CTF, mobile category.

## Statement and artefacts

See the original challenge files and images in this directory.

## Recognition signals

- (see resolution method below)

## Resolution method

# Sherlock 7

![Screenshot From 2025-11-09 09-41-04.png](img/Screenshot_From_2025-11-09_09-41-04.png)

They say in the that the suspect consult his hackbook within a web app. So I went into the “data/data/com.android.chrome” path and by searching I found this database

```
data/data/com.android.chrome/app_chrome/Default/Offline Pages/metadata/OfflinePages.db
```

I found some offline url pages

![Screenshot From 2025-11-05 17-50-22.png](img/Screenshot_From_2025-11-05_17-50-22.png)

And we can see the hackbook site mentioned in the challenge description

I got the path of the offline page

![Screenshot From 2025-11-05 17-50-40.png](img/Screenshot_From_2025-11-05_17-50-40.png)

And opened it.

![Screenshot From 2025-11-05 17-51-31.png](img/Screenshot_From_2025-11-05_17-51-31.png)

We can clearly see the “HACK BOOK” page the suspect browsered and we count that 3 people payed for his ransom

**FLAG:** SADC{3}

## Flag

SADC{3}

## Lessons and reusable patterns

- (see resolution method above)
