__author__ = 'will'

import subprocess

def read_rssi():
    # try:
    #     p = subprocess.Popen(["awk", "NR==3", "/proc/net/wireless"], stdout=subprocess.PIPE)
    #     out, err = p.communicate()
    #     out = out.replace("  ", " ").replace("  ", " ")
    #     link = out.split(" ")[3]
    #     return link
    # except:
    #     return "0"
    fp = open("/proc/net/wireless")
    for i, line in enumerate(fp):
        if i == 2:
            out = line.replace("  ", " ").replace("  ", " ")
            fp.close()
            link = out.split(" ")[3]
            return link
