# NAME:		Bryan Tang
# EMAIL: 	tangtang1228@ucla.edu
# ID:    	605318712

CC = gcc
CFLAGS = -Wall -Wextra -g
TARGET=lab3a

default:
	$(CC) $(CFLAGS) $(TARGET).c -o $(TARGET)

clean: 
	rm -rf $(TARGET) *.tar.gz

dist: graphs
	tar -cvzf $(TARGET)-605318712.tar.gz ext2_fs.h $(TARGET).c Makefile README
