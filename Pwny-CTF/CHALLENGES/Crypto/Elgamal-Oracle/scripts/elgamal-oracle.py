#!/usr/local/bin/python3
import os
import sys
import random
from Crypto.Util.number import getPrime

FLAG = os.environ['FLAG']

def group_setup():
    '''Setup a prime and a group element of 2 for Diffie-Hellman.'''
    p = getPrime(1000)
    g = 2
    return p, g

def dh_alice_setup(p,g):
    '''Alice's Diffie-Hellman computations.'''
    a = random.randint(2, p-1)
    A = pow(g, a, p)
    return a, A

def dh_bob_setup(p, A, g):
    '''Bob's Diffie-Hellman stuff, and shares secret.'''
    b = random.randint(2,p-1)
    B = pow(g, b, p)
    ss = pow(A, b, p)
    return ss, B

def alice_elgamal_decrypt(g, p, a):
    '''An Elgamal decryption oracle you can use once with input
    ciphertext (c1,c2). Output is the Elgamal decryption result.'''
    c1 = int(input("Enter c1:\n"), 16)
    c2 = int(input("Enter c2:\n"), 16)
    if c2 != 1:
        print(hex((pow(pow(c1,a,p), -1, p)*c2 % p)))
        return
    print("Do you take me for a fool, sir?")
    sys.exit()

p, g = group_setup()
a, A = dh_alice_setup(p, g)
shared_secret, B = dh_bob_setup(p, A, g)

print("p = ", hex(p))
print("A = ", hex(A))
print("B = ", hex(B))

alice_elgamal_decrypt(g, p, a)

your_guess = int(input("Guess the shared secret:\n"), 16)
if your_guess == shared_secret:
    print(FLAG)
else:
    print("I'm sorry Dave, I'm afraid that's incorrect.")
