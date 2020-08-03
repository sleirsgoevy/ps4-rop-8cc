#include <printf/printf.h>
#include <ps4/errno.h>
#include <sys/socket.h>
#include <netinet/in.h>

extern int ps4_printf_fd;

int main()
{
    ps4_printf_fd = socket(AF_INET, SOCK_STREAM, 0);
    struct sockaddr_in addr = {
        .sin_family = AF_INET,
        .sin_addr = {.s_addr = YOURIP},
        .sin_port = 0xd204,
    };
    connect(ps4_printf_fd, &addr, sizeof(addr));
    printf("Hello, world!\n");
    return 0;
}
