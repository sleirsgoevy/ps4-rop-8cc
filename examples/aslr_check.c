#include <unistd.h>
#include <printf/printf.h>

unsigned long long __builtin_gadget_addr(const char*);

int main()
{
    int pid = getpid();
    unsigned long long saveall_addr = __builtin_gadget_addr("$ saveall_addr");
    printf("pid=%d saveall_addr=%llx\n", pid, saveall_addr);
    return 0;
}
