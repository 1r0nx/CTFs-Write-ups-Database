# pwntools — Pwny-CTF (script de solve)
from pwn import *

filename = "magic_words.txt"
HOST, PORT = "chal.sigpwny.com", 5050
context.log_level = "debug"
res = b""


while b"sigpwny" not in res:
    io = remote(HOST, PORT)
    with open(filename, "r") as file:
        magic_words = [line.strip() for line in file]

    if magic_words == []:
        io.sendlineafter(b"word? ", b"...")
        res = io.recvline()
        magic_word = res.decode().split("the word was ", 1)[1].strip()
        print(f"Magic word was: {magic_word}")
        with open(filename, "a") as file:
            file.write(magic_word + "\n")
        io.close()
        continue
    else:
        for i,magic_word in enumerate(magic_words):
            print(f"Sending: {magic_word}")
            io.sendlineafter(b"word? ", magic_word.encode())
            if i == len(magic_words) - 1:
                io.sendlineafter(b"word? ", b"...")
                res = io.recvline()
                magic_word = res.decode().split("the word was ", 1)[1].strip()
                print(f"Magic word was: {magic_word}")
                with open(filename, "a") as file:
                    file.write(magic_word + "\n")
                io.close()    
                continue 

