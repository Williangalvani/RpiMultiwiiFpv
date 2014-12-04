__author__ = 'will'

import subprocess

def read_rssi():
    p = subprocess.Popen(["awk", "NR==3", "/proc/net/wireless"], stdout=subprocess.PIPE)
    out, err = p.communicate()
    out = out.replace("  ", " ").replace("  ", " ")
    link = out.split(" ")[3]
    return link
