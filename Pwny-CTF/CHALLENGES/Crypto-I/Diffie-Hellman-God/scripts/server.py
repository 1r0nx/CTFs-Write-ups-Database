#!/usr/bin/env python3

import csv
import random

def main():
    g = 2    

    p = 2410312426921032588552076022197566074856950548502459942654116941958108831682612228890093858261341614673227141477904012196503648957050582631942730706805009223062734745341073406696246014589361659774041027169249453200378729434170325843778659198143763193776859869524088940195577346119843545301547043747207749969763750084308926339295559968882457872412993810129130294592999947926365264059284647209730384947211681434464714438488520940127459844288859336526896320919633919

    # load primes
    primes: list[int] = []
    with open("primes.csv", "r") as primelist:
        csvreader = csv.reader(primelist)
        for row in csvreader:
            primes.append(int(row[0]))
    
    print("Alice has sent you her public key.")
    print("You've also been given your private key.")
    print("Now calculate your shared secret.")
    print()
    print(f"g = {g}")
    print(f"p = {p}")

    for i in range(1000):
        a = int(random.choice(primes))
        b = int(random.choice(primes))
        while a == b:
            p2 = int(random.choice(primes))

        A = pow(g, a, p)
        shared = pow(A, b, p)
        print(f"b = {b}")
        print(f"A = {A}")
        
        x = input(" > ")
        inp = x.split()
        if int(inp[0]) != shared:
            print("Wrong secret")
            exit(-1)

        print()

    with open("flag.txt", "r") as flag_file:
        flag = flag_file.read()
        print(f"Congrats! Here's the flag: {flag}")

if __name__ == "__main__":
    main()
