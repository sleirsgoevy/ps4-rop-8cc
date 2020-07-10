#include <stdio.h>
#include <stddef.h>

#ifdef __PS4__
#include <ps4/mmap.h>
#else
#include <sys/mman.h>
#endif

#include "extcall.h"

int pthread_create(void** retval, void* attr, void*(*start_routine)(void*), void* arg);

int pthread_create__rop(void** retval, void* attr, void*(*start_routine)(void*), void* arg)
{
    char* new_stack = mmap(0, 65536, PROT_READ | PROT_WRITE, MAP_SHARED | MAP_ANONYMOUS, -1, 0) + 65536;
    int extcall_sz = sizeof(extcall_t);
    extcall_sz -= 1;
    extcall_sz |= 15;
    extcall_sz += 1;
    extcall_t* x = (extcall_t*)(new_stack-extcall_sz);
    create_extcall(*x, start_routine, new_stack-extcall_sz-16, arg);
    return pthread_create(retval, attr, extcall_gadget, *x);
}
