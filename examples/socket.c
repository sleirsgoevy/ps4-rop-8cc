#include <stdint.h>
#include <sys/socket.h>
#include <unistd.h>
#include <fcntl.h>
#include <netinet/in.h>
#include <printf/printf.h>
#include <ps4/errno.h>

int socketex(const char* name, int domain, int type, int protocol);

struct sockaddr_in_
{
    uint8_t sin_len;
    uint8_t sin_family;
    uint16_t sin_port;
    struct
    {
        uint32_t s_addr;
    } sin_addr;
    char padding[8];
};

int main()
{
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    struct sockaddr_in_ addr = {16, AF_INET, 0xd204, 0};
    bind(sock, &addr, sizeof(addr));
    listen(sock, 1);
    socklen_t l = sizeof(addr);
    int sock2 = accept(sock, &addr, &l);
    write(sock2, "hello i am ps4\n", 16);
    close(sock2);
    close(sock);
    return 0;
}
