# ICMP-exfiltration — Root-Me (script de solve)
import subprocess

cmd = [
    "tshark",
    "-r",
    "ch50/capture.pcapng",
    "-Y",
    "icmp.type==8",
    "-T",
    "fields",
    "-e",
    "frame.time_epoch",
]

times = subprocess.check_output(cmd, text=True).splitlines()

previous = None
message = ""

for line in times:

    t = float(line)

    if previous is not None:
        if t - previous > 1.4:
            message += " "

    sec = int(t) % 60

    if sec == 0:
        message += "/"
    elif sec % 2 == 0:
        message += "."
    else:
        message += "-"

    previous = t

print(message)