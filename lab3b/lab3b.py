# NAME:		Bryan Tang, Zhengtong Liu
# EMAIL: 	tangtang1228@ucla.edu, ericliu2023@g.ucla.edu
# ID:    	605318712, 505375562

import sys


if len(sys.argv) != 2:
    sys.stderr.write("Invalid Argument(s)\n")
    exit(1)

try:
    input_file = open(sys.argv[1], "r")
except:
    sys.stderr.write("cannot open the file\n")
    exit(1)




