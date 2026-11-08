#!/bin/bash

# Flag located at /flag.txt

while true
do
	echo "Enter input:"
	read input
	eval "$input" > /dev/null
done
