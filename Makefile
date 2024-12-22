# 定义变量
CC = gcc
CFLAGS = -Wall -g
TARGET = my_program

# 默认目标
all: $(TARGET)

# 链接目标程序
$(TARGET): main.o utils.o
    $(CC) $(CFLAGS) -o $(TARGET) main.o utils.o

# 编译源文件
main.o: main.c
    $(CC) $(CFLAGS) -c main.c

utils.o: utils.c
    $(CC) $(CFLAGS) -c utils.c

# 清理生成的文件
clean:
    rm -f $(TARGET) *.o

# 伪目标
.PHONY: all clean
