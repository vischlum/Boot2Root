#!/bin/env python3
"""
 ______                 ___            __                          __     
/_  __/__ ___ ___ _    / _ )___  __ __/ /____  __ _________  __ __/ /____ 
 / / / -_) _ `/  ' \  / _  / _ \/ // / __/ _ \/ // / __/ _ \/ // / __/ -_)
/_/  \__/\_,_/_/_/_/ /____/\___/\_,_/\__/\___/\_,_/_/  \___/\_,_/\__/\__/ 
"""

from pathlib import Path
import re
import os

os.system("tar -xf fun");

getnum = re.compile(r'//\s*file\s*(\d+)')

def getdata(filename):
    """read the filename and return a tuple with the file number and its content"""
    with open(filename) as f:
        data = f.read()
        return (int(getnum.search(data).group(1)), data)

fragments = [getdata(filename) for filename in Path('./ft_fun').rglob('*.pcap')]
fragments.sort();

# write all the fragments in solver.c
with open('solver.c', 'w') as out:
    for chunk_id, chunk_text in fragments:
        out.write(chunk_text + '\n')

os.system("gcc solver.c -o solver && ./solver && echo '\n'");