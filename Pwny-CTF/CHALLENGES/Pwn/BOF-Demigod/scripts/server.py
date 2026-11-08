#!/usr/bin/env python3
import string
import random

# TODO Change this to allow for arbitrary sizes
def make_buf():
  before = (random.randrange(1,3) * 16)
  after = (random.randrange(1,3) * 16)
  buf = b'\x00' * before + b"Beep" + b"CHANGEME" + b"Borp" + b'\x00' * after
  return buf,before,after

def print_buffer(b):
    for i in range(len(b)):
      if i % 16 == 0:
        print("\n" + hex(i)[2:].zfill(8) + ': ',end='')
        print(hex(b[i])[2:].zfill(2),end='')
      elif i % 2 == 0:
        print(' ',end='')
        print(hex(b[i])[2:].zfill(2),end='')
      else:
        print(hex(b[i])[2:].zfill(2),end='')

    if (len(b) % 16 != 0):
      for i in range(len(b), len(b) + (16 - len(b) % 16)):
        if i % 2 == 0:
          print(' 00',end='')
        else:
          print('00',end='')
    print('')

def check_solution(b,before,resp):
    newbuf = resp.encode('utf-8') + b[len(resp):]
    beep = newbuf[(before ):(before  + 4)]
    borp = newbuf[(before + 12):(before  + 16)]
    changeme = newbuf[(before + 4):(before + 12)]
    # print(beep,borp,changeme)
    if beep == b'Beep' and borp == b'Borp' and changeme != b'CHANGEME':
      return True
    print("\nYou missed it! Here was the buffer!",end='')
    print_buffer(resp.encode('utf-8') + newbuf[len(resp):])
    return False

def gen_challenge():
    buf,before,after = make_buf()
    print_buffer(buf)
    print('Input > ',end='')
    resp = input()
    return check_solution(buf,before,resp)
      

def main():
  for i in range(100):
    if gen_challenge() == True:
      print("Good Job keep going")
    else:
      print("Exiting...")
      exit()
    
  with open("flag.txt", "r") as flag_file:
      print("You did it! Here is your flag: " + flag_file.read())
      
      
        
if __name__ == "__main__":
    main()