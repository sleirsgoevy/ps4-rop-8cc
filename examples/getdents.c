#include <stdint.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <printf/printf.h>
#include <ps4/errno.h>

struct dirent {
	uint32_t d_fileno;
	uint16_t d_reclen;
	uint8_t d_type;
	uint8_t d_namlen;
	char d_name[255 + 1];
};

int getdents(int fd, char* buf, int cnt);

int main()
{
    int fd = open("/dev", O_RDONLY);
    if(fd < 0)
    {
        printf("open failed: %d\n");
        return 1;
    }
    char dearr[0x1001];
    int l;
    while((l = getdents(fd, dearr, 0x1000)) > 0)
    {
        int offset = 0;
        while(offset < l)
        {
            struct dirent* d = (struct dirent*)(dearr+offset);
            offset += d->d_reclen;
            char c = d->d_name[d->d_namlen];
            d->d_name[d->d_namlen] = 0;
            printf("* %s\n", d->d_name);
            d->d_name[d->d_namlen] = c;
        }
    }
    return 0;
}
