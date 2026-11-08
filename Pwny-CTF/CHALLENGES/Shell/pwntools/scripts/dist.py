#!/usr/bin/python3
import random
import sys

flag = "XXXXXXXXXXXXXXXXXXXXX"
wordlist = open("wordlist.txt").read().splitlines()

status = 1	# 0 = lose, 1 = win

for i in range(len(wordlist)):
	sys.stdout.write(f"What is the {i+1}th magic word? ")
	sys.stdout.flush()
	x = input()
	if x != wordlist[i]:
		status = 0
		break

if (status == 1):
	print(flag)
else:
	print("WRONG WORD! the word was " + wordlist[i] + "\nGoodbye...")
