# NAME:		Bryan Tang, Zhengtong Liu
# EMAIL: 	tangtang1228@ucla.edu, ericliu2023@g.ucla.edu
# ID:    	605318712, 505375562

import sys

isConsistent = True
bfree = []
ifree = []
indir = []
diren = []
inodes = []

inode_link_counts = {} # key: inode_num; value: link counts (theoretical)
inode_dir_name = {} # key: inode_num; value: dir_name
inode_ref_array = {} # key: inode_num; value: reference counts (actual)
inode_par_array = {} # key: child_inode_num; value: parent_inode_num
blockDict = {} # key: block number; value: [inode_num, level]

numOfBlocks = 0
numOfInodes = 0
blocks_count = 0
inodes_count = 0
block_size = 0
inode_size = 0

non_reserved_block_start = 0

def read_csv(file):

    lines = file.readlines()

    for line in lines:
        fields = line.split(",")
        Type = fields[0]

        if Type == 'SUPERBLOCK':
            blocks_count = int(fields[1])
            inodes_count = int(fields[2])
            block_size = int(fields[3])
            inode_size = int(fields[4])
        elif Type == 'GROUP':
            numOfBlocks = int(fields[2])
            numOfInodes = int(fields[3])
            bg_inode_table = int(fields[8])

            non_reserved_block_start = bg_inode_table + inode_size * numOfInodes / block_size

        elif Type == 'BFREE':
            bfree.append(int(fields[1]))
        elif Type == 'IFREE':
            ifree.append(int(fields[1]))
        elif Type == 'INODE':
            inodeNum = int(fields[1])
            # fileType = fields[2]
            # mode = int(fields[3])
            # owner = int(fields[4])
            # group = int(fields[5])
            linkCount = int(fields[6])
            inode_link_counts[inodeNum] = linkCount

            for i in range(12,27):
                blockNum = int(fields[i])

                if blockNum == 0: #skip if 0
                    continue
                if i < 24:
                    blockType = 'BLOCK'
                    offset = 0
                    level = 0
                elif i == 24:
                    blockType = 'INDIRECT BLOCK'
                    offset = 12
                    level = 1
                elif i == 25:
                    blockType = 'DOUBLE INDIRECT BLOCK'
                    offset = 12 + 256
                    level = 2
                elif i == 26:
                    blockType = 'TRIPLE INDIRECT BLOCK'
                    offset = 12 + 256 + 256**2
                    level = 3
                
                block_consistency_audits(blockType, blockNum, inodeNum, offset, level)

        elif Type == 'INDIRECT':
            inodeNum = int(fields[1])
            level = int(fields[2])
            blockNum = int(fields[4])

            if level == 1:
                blockType = 'INDIRECT BLOCK'
                offset = 12
            elif level == 2:
                blockType = 'DOUBLE INDIRECT BLOCK'
                offset = 12 + 256
            elif level == 3:
                blockType = 'TRIPLE INDIRECT BLOCK'
                offset = 12 + 256 + 256**2
                
            block_consistency_audits(blockType, blockNum, inodeNum, offset, level)

        
        elif Type == 'DIRENT':
            parentInodeNum = int(fields[1])
            # offset = int(fields[2])
            refInodeNum = int(fields[3])
            # entryLength = int(fields[4])
            # nameLength = int(fields[5])
            dirName = fields[6]
            # slice off the '\n' character
            dirName = dirName[:-1]

            directory_consistency_audits(parentInodeNum, refInodeNum, dirName)
        
    # check for allocation, duplication, and unreference of blocks
    block_check_audits()

    # check for allocation of inodes
    inode_allocation_audits()

    directory_check_audits()



def block_consistency_audits(block_type, block_num, inode_num, offset, level):
    # valid
    if block_num < 0 or block_num > blocks_count:
        print('INVALID ' + block_type + ' ' + str(block_num) + ' IN INODE ' + str(inode_num) + ' AT OFFSET ' + str(offset))
        isConsistent = False
    # reserved
    if block_num < non_reserved_block_start:
        print('RESERVED ' + block_type + ' ' + str(block_num) + ' IN INODE ' + str(inode_num) + ' AT OFFSET ' + str(offset))
        isConsistent = False
    # allocated

    # duplicated

    if block_num in blockDict:
        blockDict[block_num].append([inode_num, level])
    else:
        blockDict[block_num] = [[inode_num, level]]
    return

def inode_allocation_audits():
    for k in range(inodes_count):
        index = k + 1
        if (index in ifree) and (index in inode_link_counts):
            print('ALLOCATED INODE ' + str(index) + ' ON FREELIST')
            isConsistent = False
        if (index not in ifree) and (index not in inode_link_counts):
            print('UNALLOCATED INODE ' + str(index) + ' NOT ON FREELIST')
            isConsistent = False

    return


def directory_check_audits():
    for child_inode in inode_dir_name:
        # not sure
        dir_name = inode_dir_name[child_inode]
        parent_inode = inode_par_array[child_inode]

        if (child_inode in ifree):
            print('DIRECTORY INODE ' + str(parent_inode) + ' NAME ' + str(dir_name) + ' UNALLOCATED INODE ' + str(child_inode))
            isConsistent = False
        
        # not sure
        if (dir_name == "'..'") and child_inode != parent_inode:
            print('DIRECTORY INODE ' + str(parent_inode) + ' NAME ' + str(dir_name) + ' LINK TO INODE ' + str(child_inode))
            isConsistent = False

    for child_inode in inode_link_counts:

        link_counts = inode_link_counts[child_inode]

        actual_link = 0
        if child_inode in inode_ref_array:
            actual_link = inode_ref_array[child_inode]
        
        if actual_link != link_counts:
            print('INODE ' + str(child_inode) + ' HAS ' + str(actual_link) + ' BUT LINKCOUT IS ' + str(link_counts))
            isConsistent = False
        
    

def directory_consistency_audits(parent_inode_num, inode_num, dir_name):

    inode_dir_name[inode_num] = str(dir_name)
    # valid
    if inode_num < 1 or inode_num > inodes_count:
        print('DIRECTORY INODE ' + str(parent_inode_num) + ' NAME ' + str(dir_name) + ' INVALID INODE ' + str(inode_num))
        isConsistent = False
    # current match
    if str(dir_name) == "'.'" and parent_inode_num != inode_num:
        print('DIRECTORY INODE ' + str(parent_inode_num) + ' NAME ' + str(dir_name) + ' LINK TO ' + str(inode_num) + ' SHOULD BE ' + str(parent_inode_num))
        isConsistent = False
    # not sure
    if str(dir_name) != "'.'" and str(dir_name) != "'..'":
        if inode_num in inode_ref_array:
            inode_ref_array[inode_num] = inode_ref_array[inode_num] + 1
        else:
            inode_ref_array[inode_num] = 1

    inode_par_array[inode_num] = parent_inode_num
    return


def block_check_audits():
    # check allocation and reference
    for k in range(blocks_count):
        index = k + 1
        if (index in blockDict) and (index in bfree):
            print('ALLOCATED BLOCK ' + str(index) + ' ON FREELIST')
            isConsistent = False
        if (index not in blockDict) and (index not in bfree):
            print('UNREFERENCED BLOCK ' + str(index))
            isConsistent = False

    # check duplication
    for blk in blockDict:
        if len(blockDict[blk]) > 1:
            isConsistent = False
            for piece in blockDict[blk]:
                inode_num = int(piece[0])
                level = int(piece[1])
                if level == 1:
                    blockType = 'INDIRECT BLOCK'
                    offset = 12
                elif level == 2:
                    blockType = 'DOUBLE INDIRECT BLOCK'
                    offset = 12 + 256
                elif level == 3:
                    blockType = 'TRIPLE INDIRECT BLOCK'
                    offset = 12 + 256 + 256**2
                
                print('DUPLICATE ' + blockType + ' ' + str(blk) + ' IN INODE ' + str(inode_num) + ' AT OFFSET ' + str(offset))
        
    return


def main():
    if len(sys.argv) != 2:
        sys.stderr.write("Invalid Argument(s)\n")
        exit(1)

    try:
        input_file = open(sys.argv[1], "r")
    except:
        sys.stderr.write("cannot open the file\n")
        exit(1)

    read_csv(input_file)

    if isConsistent:
        exit(0)
    else:
        exit(2)


if __name__ == '__main__':
    main()
