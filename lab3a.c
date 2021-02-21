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
    blockSize = 1024 << sb.s_log_block_size;
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
    numOfGroups = sb.s_blocks_count / sb.s_blocks_per_group + 1;

    group = malloc(numOfGroups * sizeof(struct ext2_group_desc));

    for (int i = 0; i < numOfGroups; i++){
        if(pread(fd, &group[i], sizeof(struct ext2_group_desc), SB_OFFSET + BLOCK_SIZE + i * sizeof(struct ext2_group_desc)) < 0){
            pread_error();
        }
        // if the last group, will contain the remainder of the blocks
        int blocksPerGroup = (i == numOfGroups-1) ? (sb.s_blocks_count % sb.s_blocks_per_group) : sb.s_blocks_per_group;
        int inodesPerGroup = (i == numOfGroups-1) ? (sb.s_inodes_count % sb.s_inodes_per_group) : sb.s_inodes_per_group;
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

void get_time_GMT(time_t t, char* buffer)
{
    time_t to_convert = t;
    struct tm ts = *gmtime(&to_convert);
    strftime(buffer, 80, "%m/%d/%y %H:%M:%S", &ts);
}

unsigned long get_offset (int block)
{
    return (unsigned long) BLOCK_SIZE * block;
}


void scan_free_block(int num, unsigned int block)
{
    unsigned int index = sb.s_first_data_block + sb.s_blocks_per_group * num;
    char* bitmap = (char *) malloc(BLOCK_SIZE);
    unsigned long offset = get_offset(block);
    if (pread(fd, bitmap, BLOCK_SIZE, offset) < 0) {
        pread_error();
    }
    unsigned int j, k;
    for (j = 0; j < BLOCK_SIZE; j++)
    {
        char c = bitmap[j];
        for (k = 0; k < 8; k++)
        {
            // note that 1 indicates the block is used
            // o indicates the block is free
            int bit = c & 1;
            if (!bit)
                fprintf(stdout, "BFREE,%d\n", index);
            // shift the c to the left to get the next bit
            c = c >> 1;
            index++;  
        }
    }
    free(bitmap);
}

char get_filetype (__u16 i_mode)
{
    char file_type;
    uint16_t file_descriptor = (i_mode >> 12) << 12;
    if (file_descriptor == 0x8000)
        file_type = 'f';
    else if (file_descriptor == 0x4000)
        file_type = 'd';
    else if (file_descriptor == 0xa000)
        file_type = 's';
    else
        file_type = '?';
    return file_type;
}

void inode_summary (unsigned int inode_table_index, unsigned int id, unsigned int num_inode)
{

    unsigned long offset = get_offset(inode_table_index) + sizeof(inode) * id;
    if (pread(fd, &inode, sizeof(inode), offset) < 0)
        pread_error();
    
    char file_type = get_filetype(inode.i_mode);



    char creation_time[20];
    char modified_time[20];
    char access_time[20];
    get_time_GMT(inode.i_ctime, creation_time);
    get_time_GMT(inode.i_mtime, modified_time);
    get_time_GMT(inode.i_atime, access_time);

    fprintf(stdout, "INODE,%d,%c,%o,%d,%d,%d,%s,%s,%s,%d,%d",
        num_inode, // the inode number
        file_type, // the file type
        inode.i_mode & 0xFFF, // the lower 12 bits of imode
        inode.i_uid, // owner uid
        inode.i_gid, // group id
        inode.i_links_count, // links count
        creation_time, // creation time
        modified_time, // modified time
        access_time, // access time
        inode.i_size, // file size
        inode.i_blocks // num of blocks
    );
    
    for (unsigned int k = 0; k < 15; k++)
    {
        fprintf(stdout, ",%u", inode.i_block[k]);
    }
    fprintf(stdout, "\n");

    if (file_type == 'd')
    {
        // print directory
    }

    // indirect
    if (inode.i_block[EXT2_IND_BLOCK] != 0)
    {
        // single indirect block
    }

    if (inode.i_block[EXT2_DIND_BLOCK] != 0)
    {
        // double indirect block
    }
    if (inode.i_block[EXT2_TIND_BLOCK] != 0)
    {
        // triple indirect block
    }



}


// num stands for the index of group
void scan_inode (int num, int block, int inode_table_index)
{

}

void directory_entries()
{

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