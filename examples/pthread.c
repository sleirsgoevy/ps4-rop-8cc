#include <librop/pthread_create.h>
#include <printf/printf.h>

void subthread(void* o)
{
    int* flag_p = (int*)o;
    printf("subthread!\n");
    *flag_p = 179;
}

int main()
{
    void* thr_ptr;
    int flag = 0;
    pthread_create(&thr_ptr, NULL, subthread, &flag);
    while(!flag);
    printf("flag = %d\n", flag);
    return 0;
}
