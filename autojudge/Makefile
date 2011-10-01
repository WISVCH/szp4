CC=gcc
CFLAGS=-Wall -Wextra -Werror -O2

all: watchdog check_float

watchdog: watchdog.c
	$(CC) $(CFLAGS) -m32 -o watchdog watchdog.c

check_float: check_float.c
	$(CC) $(CFLAGS) -o check_float check_float.c

clean:
	rm -f watchdog check_float

