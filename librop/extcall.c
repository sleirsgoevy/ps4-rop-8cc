unsigned long long __builtin_gadget_addr(const char*);

typedef unsigned long long extcall_t[39];

void create_extcall(extcall_t arr, void(*func)(void), void* emu_stack, void* opaque)
{
    unsigned long long* st = emu_stack;
    // pivot-related stuff
    arr[0] = arr + 1;
    arr[1] = __builtin_gadget_addr("$pivot_addr");
    arr[7] = arr + 8;
    arr[8] = opaque;
    // store arguments
    arr[9] = __builtin_gadget_addr("pop rax");
    arr[10] = st - 6;
    arr[11] = __builtin_gadget_addr("mov [rax], rdi");
    arr[12] = __builtin_gadget_addr("mov rax, rsi");
    arr[13] = __builtin_gadget_addr("pop rsi");
    arr[14] = st - 5;
    arr[15] = __builtin_gadget_addr("mov [rsi], rax");
    arr[16] = __builtin_gadget_addr("mov rax, rdx");
    arr[17] = __builtin_gadget_addr("pop rsi");
    arr[18] = st - 4;
    arr[19] = __builtin_gadget_addr("mov [rsi], rax");
    arr[20] = __builtin_gadget_addr("mov rax, rcx");
    arr[21] = __builtin_gadget_addr("pop rsi");
    arr[22] = st - 3;
    arr[23] = __builtin_gadget_addr("mov [rsi], rax");
    arr[24] = __builtin_gadget_addr("pop rdi");
    arr[25] = st - 4;
    arr[26] = __builtin_gadget_addr("mov [rdi + 0x10], r8");
    arr[27] = __builtin_gadget_addr("pop rdi");
    arr[28] = st - 3;
    arr[29] = __builtin_gadget_addr("mov [rdi + 0x10], r9");
    // load virtual stack pointer
    arr[30] = __builtin_gadget_addr("pop rdi");
    arr[31] = st - 7;
    // set return address
    arr[32] = __builtin_gadget_addr("pop rax");
    arr[33] = arr + 37;
    arr[34] = __builtin_gadget_addr("mov [rdi], rax");
    // jump to function
    arr[35] = __builtin_gadget_addr("pop rsp");
    arr[36] = func;
    // mov return value to rax
    arr[37] = __builtin_gadget_addr("mov rax, rcx");
    // the pivot gadget pushed a stack frame, so we can return by simply doing `leave ; ret`
    arr[38] = __builtin_gadget_addr("mov rsp, rbp ; pop rbp");
}
