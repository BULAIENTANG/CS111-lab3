/*
 NAME:	Bryan Tang
 EMAIL: tangtang1228@ucla.edu
 ID:    605318712
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <limits.h>
#include <stdint.h>
#include <time.h>
#include <fcntl.h>
#include "ext2_fs.h"

#define SB_OFFSET 1024
#define BLOCK_SIZE 1024

int fd = -1;
struct ext2_super_block sb;
struct ext2_inode inode;
struct ext2_group_desc* group;
struct ext2_dir_entry dir_entry;

uint32_t blockSize;
uint32_t inodeSize;

int numOfGroups;

void pread_error()
{
    fprintf(stderr, "Error with pread: %s\n", strerror(errno));
    exit(1);
}

void superblock_summary() {
    if(pread(fd, &sb, sizeof(struct ext2_super_block), SB_OFFSET) < 0){
        pread_error();
    }
    blockSize = 1024 << sb.log_block_size;
    fprintf(stdout, "SUPERBLOCK,%d,%d,%d,%d,%d,%d,%d\n", 
		sb.s_blocks_count,      //number of blocks
		sb.s_inodes_count,      //number of inodes
		blockSize,	            //block size
		sb.s_inode_size,        //inode size
		sb.s_blocks_per_group,  //blocks per group
		sb.s_inodes_per_group,  //inodes per group
		sb.s_first_ino          //first non-reserved inode 
	);
}

void group_summary() {
    numOfGroups = super.s_blocks_count / super.s_blocks_per_group + 1;

    group = malloc(numOfGroups * sizeof(struct ext2_group_desc));

    for (int i; i < numOfGroups; i++){
        if(pread(fd, &group[i], sizeof(struct ext2_group_desc), SB_OFFSET + BLOCK_SIZE + i * sizeof(struct ext2_group_desc)) < 0){
            pread_error();
        }
        // if the last group, will contain the remainder of the blocks
        int blocksPerGroup = (i == numOfGroups-1) ? (super.s_blocks_count % super.s_blocks_per_group) : sb.s_blocks_per_group;
        int inodesPerGroup = (i == numOfGroups-1) ? (super.s_inodes_count % super.s_inodes_per_group) : sb.s_inodes_per_group;
        fprintf(stdout, "GROUP,%d,%d,%d,%d,%d,%d,%d,%d\n",
            i, //group number
            blocksPerGroup, //total number of blocks in this group
            inodesPerGroup, //total number of inodes in this group
            group[i].bg_free_blocks_count, //number of free blocks 
            group[i].bg_free_inodes_count, //number of free inodes
            group[i].bg_block_bitmap, //block number of free block bitmap for this group
            group[i].bg_inode_bitmap, //block number of free inode bitmap for this group
            group[i].bg_inode_table //block number of first block of i-nodes in this group
        );
    }
}

int main(int argc, char* argv[]){
    if(argc != 2){
        fprintf(stderr, "%s\n", "Bad arguments");
        exit(1);
    }

    if((fd = open(argv[1], O_RDONLY)) < 0)
    {
        fprintf(stderr, "%s\n", "Fail to mount disk image" );
        exit(2);
    }
    ///
}