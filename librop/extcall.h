#pragma once

unsigned long long __builtin_gadget_addr(const char* s);

#define extcall_gadget ((void(*)(void))__builtin_gadget_addr("$jop_frame_addr"))

typedef unsigned long long extcall_t[39];

void create_extcall(extcall_t ec, void(*func)(void), void* stack, void* opaque);

// call native function pointer from ROP
unsigned long long rop_call_funcptr(void(*)(void), ...);
