---
title: "Fatal"
ctf: "2025_SADC-NextGenCyber-CTF"
category: "Web"
difficulty: "Not specified"
points: 0
techniques: []
tools: []
keywords: []
status: "solved"
has_script: false
source: "2025_SADC-NextGenCyber-CTF/Web/Fatal.md"
---

## Summary

Challenge **Fatal** from the 2025_SADC-NextGenCyber-CTF CTF, web category.

## Statement and artefacts

See the original challenge files; provided artefacts are not copied.

## Recognition signals

- (see resolution method below)

## Resolution method

# Fatal [500pts]

![Page](img/fat1.png)

Very nice story but first i explore the source  code there are no link for anything and then let's check in the side of burp

Got something here
![fact](img/fat2.png)
this cookie seem like the patern of php serialized objects

![serialized patern](img/dese.png)

alright let's check it in [CyberChef](https://gchq.github.io/CyberChef/)

![good find](img/fat3.png)

It look like it's the web page that is loaded let try to load `/etc/passwd` file to see what happen
![poisoned](img/fat4.png)

notice that we modify the last s value also because it need to macth with the number of characters of the contains of the `""`!

Note: there are `s` because the content is a strings!
So  
  `/etc/passwd` is 11 characters so we place `O:11:"ArcaneModel":1:{s:10:"armageddon";s:11:"/etc/passwd";}`

let encode and send it to see the result:

![boom](img/fat5.png)

Very nice we can read abritary file with this alright let's get our flag

![no flag](img/fat6.png)

Why??
May be the name is not correct i search anywhere nothing for me and for the moment i take a break and come back
We known that we have an LFI (Local File Inclusion) but how can we get an RCE (Remote Code execution) to find how flag??

Some googling...

Here a good ressources for Web Security [PayloadAllThings](https://swisskyrepo.github.io/PayloadsAllTheThings/)

![good ressources](img/fat7.png)

I check everyone the one who is possible is by log file

![access log file](img/fat9.png)

- We know that the server is nginx
- We know that nginx log are  located in `/var/log/nginx/`
- And we can access to the `access.log` file
  
Nice so what to do now
let make  our malicious request to the server

![payload](img/fat8.png)

and then
![executed](img/fat10.png)

boom!!!

We know now that we can execute code in the log file just by replacing our User-Agent with malicious php code so let find our flag and read it

After searching i find the flag there
![Getting flag](img/fat11.png)
![Flag](img/fat12.png)


## Flag

Not specified

## Lessons and reusable patterns

- (see resolution method above)
