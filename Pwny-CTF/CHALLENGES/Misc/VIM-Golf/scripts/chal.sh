#!/usr/bin/env bash

cd files

cat <<'EOF'
Welcome to the challenge!

Your goal is to use VIM to create the following file (called "out.txt") in as few keystrokes as possible:

```
1 hello
2 hello
3 hello
4 hello
5 hello
6 hello
7 hello
8 hello
9 hello
```

You can record the VIM keystrokes by using the following command:

```
vim -T dumb -N -u NONE -n -c "set nomore" -c "set nocompatible" -W recording.bin
```

This records your keystrokes into the file recording.bin. You can replay the recording by using the following command:

```
vim -T dumb -N -u NONE -n -c "set nomore" -c "set nocompatible" -s recording.bin
```

Note that backspace is recorded as a special character sequence, which may mess up your recording. You can fix this by using the following command:

```
xxd -p recording.bin | tr -d '\n' | sed 's/../& /g' | sed 's/80 6b 62 /08 /g' | tr -d ' ' | xxd -r -p > recording-fixed.bin
```

To submit your recording, please use the following command:

```
xxd -p recording.bin
```

This dumps out the hex representation of your recording.

Your limit is 40 keystrokes. Good luck!

Please paste the recording here:
EOF

# read in user's recorded input
read -r recording

# check that input is hex
if ! echo "$recording" | grep -qE '^[0-9a-fA-F]+$'; then
    echo "Sorry, your recording is not in hex. Please try again."
    exit
fi

# convert backspace characters to backspace
recording_fixed=$(echo "$recording" | sed 's/../& /g' | sed 's/80 6b 62 /08 /Ig' | tr -d ' ')

# check that recording is less than 40 keystrokes (80 hex characters)
if [[ ${#recording_fixed} -gt 80 ]]; then
    echo "Sorry, your recording is too long. Please try again."
    exit
fi

# convert hex to binary
echo "$recording_fixed" | xxd -r -p > recording.bin

# replay recording
vim --not-a-term -T dumb -N -u NONE -n -c "set nomore" -c "set nocompatible" -s recording.bin > /dev/null

# check if recording is correct
cat > correct.txt <<'EOF'
1 hello
2 hello
3 hello
4 hello
5 hello
6 hello
7 hello
8 hello
9 hello
EOF

if diff -q out.txt correct.txt > /dev/null; then
    echo "Congratulations! You have completed the challenge!"
    echo "The flag is: $(cat ../flag.txt)"
else
    echo "Sorry, your recording is incorrect. Please try again."
fi

# clean up
rm -f recording.bin correct.txt out.txt
