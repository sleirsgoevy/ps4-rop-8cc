#include "../printf/printf.h"

extern char* ps4_printf_buffer;
extern int ps4_printf_fd;

void write(int fd, char* c, unsigned long long cnt);

void _putchar(char c)
{
    if(ps4_printf_fd >= 0)
        write(ps4_printf_fd, &c, 1);
    *ps4_printf_buffer++ = c;
}
