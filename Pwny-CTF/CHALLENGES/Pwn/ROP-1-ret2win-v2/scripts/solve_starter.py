#!/usr/bin/env python3

from pwn import *

exe = ELF('./chal') # elf object for the binary

host = 'chal.sigpwny.com'
port = 1337 # put the actual port here


# rop object for the binary
# this will allow you to find gadgets more easily
# pwntools rop documentation: https://docs.pwntools.com/en/stable/rop/rop.html
rop = ROP(exe)

context.arch = 'amd64' # set the architecture to 64-bit
context.binary = exe # set the binary to the elf object


#===========================================================
#                    EXPLOIT GOES HERE
#===========================================================

def solve():
    # *** START PROCESS ***
    conn = process([exe.path]) # LOCAL
    # conn = remote(host, port) # REMOTE
    
    # *** GADGETS ***
    POP_RDI = (rop.find_gadget(['pop rdi', 'ret']))[0] # example gadget (hint: this one's useful!)
    
    # you can look for more gadgets using ROPgadget: ROPgadget --binary chal
    # or using the line below (this filters out some gadgets pwntools thinks are useless)
    # print(rop.gadgets)
    
    # if you find that you are entering the win() function correctly
    # but you are segfaulting before you can get the flag, 
    # you are probably encountering a stack alignment issue - https://stackoverflow.com/questions/54393105/libcs-system-when-the-stack-pointer-is-not-16-padded-causes-segmentation-faul
    # tl;dr: weird things can happen if the stack isn't 16-byte aligned when you call certain functions
    # to fix this, you can add a ret gadget before calling the win() function
    RET = (rop.find_gadget(['ret']))[0] 
    
    # *** PAYLOAD ***
    exploit = b'A' * 0 # <-- change this to the correct padding
    exploit += b'...' # add more to the payload
    
    # remember: you want to call win() with arg1 = 0xdeadbeef and arg2 = 0xcafebabe
    # what should the registers look like to make this happen?
    
    conn.sendline(exploit) # send the payload
    
    conn.interactive() # drop to an interactive shell
    
if __name__ == '__main__':
    solve()
    


