#include "../printf/printf.h"

extern char* ps4_printf_buffer;

void _putchar(char c)
{
    *ps4_printf_buffer++ = c;
}
