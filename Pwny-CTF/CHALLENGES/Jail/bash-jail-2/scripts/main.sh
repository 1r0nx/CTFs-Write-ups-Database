#!/bin/bash

# Flag located at /flag.txt

while true
do
	echo "Enter input:"
	read input
	if (echo "$input" | grep -E -q ".*[<>()$*|AC-Zac-z]+.*")
	then
		echo "Banned character used!"
	else
		eval "$input" 
	fi
done
