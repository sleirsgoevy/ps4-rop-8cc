#include <stdio.h>
#include <stddef.h>

#ifdef __PS4__
#include <ps4/mmap.h>
#else
#include <sys/mman.h>
#endif

#include "extcall.h"

int pthread_create(void** retval, void* attr, void*(*start_routine)(void*), void* arg);

static void* wrapper(void* arg)
{
    void** o = (void**)arg;
    void(*func)(void*) = o[0];
    void* arg = o[1];
    *((volatile int*)o[2]) = 1;
    return func(arg);
}

int pthread_create__rop(void** retval, void* attr, void*(*start_routine)(void*), void* arg)
{
    char* new_stack = mmap(0, 65536, PROT_READ | PROT_WRITE, MAP_SHARED | MAP_ANONYMOUS, -1, 0);
    volatile int flag = 0;
    void* opaque[3] = {start_routine, arg, &flag};
    extcall_t ec;
    create_extcall(ec, &wrapper, new_stack+65536, &opaque);
    int ans = pthread_create(retval, attr, extcall_gadget, ec);
    if(ans) // fail
        return ans;
    // else wait for the wrapper to read arguments, so we can free opaque and extcall
    // TODO: shouldn't we free the stack when the thread exits?
    while(!flag);
    return 0;
}
