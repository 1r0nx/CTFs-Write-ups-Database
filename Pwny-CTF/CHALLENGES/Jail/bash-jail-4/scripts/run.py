#!/usr/bin/env python3

#Flag is at /flag.txt


import subprocess
import os
import string
import base64

def check_bash_file(file_contents):
    if len(file_contents) == 0: return False
    letters_used = [i for i in string.ascii_letters if i in file_contents.decode()]
    allowed_letters = "nop"
    return set(letters_used) <= set(allowed_letters)

while True:
    bash_b64 = input("Please input your bash script that you want to run (base 64 encoded please, our servers aren't capable of more complex data transfer methods at the moment...): ")
    bash_file = open("temp.sh", "w")
    filepath = os.path.realpath(bash_file.name)
    bash_script = base64.b64decode(bash_b64.encode())
    if check_bash_file(bash_script):
        print("Running bash script...")
        bash_file.write(bash_script.decode())
        bash_file.close()
        os.chmod(filepath, 0o777)
        subprocess.call([filepath], shell=True)
    else:
        print("Sorry, no running this script, seems kinda sus")
        exit()
