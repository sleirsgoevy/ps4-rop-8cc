#pragma once

#define pthread_create pthread_create__rop

int pthread_create(void** retval, void* attr, void*(*start_routine)(void*), void* arg);
