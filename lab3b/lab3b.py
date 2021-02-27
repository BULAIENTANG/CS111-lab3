# NAME:		Bryan Tang, Zhengtong Liu
# EMAIL: 	tangtang1228@ucla.edu, ericliu2023@g.ucla.edu
# ID:    	605318712, 505375562

import sys

isConsistent = False

def read_csv(file):
    bfree = []
    ifree = []
    indir = []
    diren = []
    inodes = []

    blockDict = {} # key: block number; value: [inode_num, offset, level]

    numOfBlocks = 0
    numOfInodes = 0
    blockSize = 0
    inodeSize = 0

    lines = file.readlines()

    for line in lines:
        fields = line.split(",")
        Type = fields[0]

        if Type == 'SUPERBLOCK':
            blockSize = int(fields[2])
            inodeSize = int(fields[3])
        elif Type == 'GROUP':
            numOfBlocks = int(fields[2])
            numOfInodes = int(fields[3])
        elif Type == 'BFREE':
            bfree.append(int(fields[1]))
        elif Type == 'IFREE':
            ifree.append(int(fields[1]))
        elif Type == 'INODE':
            inodeNum = int(fields[1])
            fileType = fields[2]
            mode = int(fields[3])
            owner = int(fields[4])
            group = int(fields[5])
            linkCount = int(fields[6])

            for i in range(12,27):
                blockNum = int(fields[i])

                if blockNum == 0: #skip if 0
                    continue
                if i < 24:
                    blockType = ''
                    offset = 0
                    level = 0
                if i == 24:
                    blockType = 'INDIRECT'
                    offset = 12
                    level = 1
                elif i == 25:
                    blockType = 'DOUBLE INDIRECT'
                    offset = 12 + 256
                    level = 1
                elif i == 26:
                    blockType = 'TRIPLE INDIRECT'
                    offset = 12 + 256 + 256**2
                    level = 1
                
                # blockDict[blockNum] = [[inodeNum, offset, level]]

        elif Type == 'INDIRECT':
            inodeNum = int(fields[1])
            level = int(fields[2])
            offset = int(fields[3])
            blockNum = int(fields[4])
            refblockNum = int(fields[5])
        
        elif Type == 'DIRENT':
            parentInodeNum = int(fields[1])
            offset = int(fields[2])
            refInodeNum = int(fields[3])
            entryLength = int(fields[4])
            nameLength = int(fields[5])
            dirName = fields[6]

def block_consistency_audits():

def inode_allocation_audits():

def directory_consistency_audits():

def main():
    if len(sys.argv) != 2:
        sys.stderr.write("Invalid Argument(s)\n")
        exit(1)

    try:
        input_file = open(sys.argv[1], "r")
    except:
        sys.stderr.write("cannot open the file\n")
        exit(1)


if __name__ == '__main__':
    main()

