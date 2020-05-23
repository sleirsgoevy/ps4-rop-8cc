#include <printf/printf.h>
#include <ps4/errno.h>

int fork();

int main()
{
    printf("fork() = %d\n", fork());
    printf("errno = %d\n", errno);
    return 0;
}
