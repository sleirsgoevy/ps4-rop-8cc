unsigned long long __builtin_gadget_addr(const char* s);

unsigned long long __builtin_nativecall(unsigned long long fnaddr)
{
    unsigned long long* args = &fnaddr;
    args += 2;
    unsigned long long ropchain_array[40];
    unsigned long long* ropchain = ropchain_array;
    if(!(((unsigned long long)ropchain)&15))
        ropchain++;
    ropchain[0] = __builtin_gadget_addr("pop rsi");
    ropchain[1] = ropchain+38;
    ropchain[2] = __builtin_gadget_addr("mov rax, [rdi]");
    ropchain[3] = __builtin_gadget_addr("mov [rsi], rax");
    ropchain[4] = __builtin_gadget_addr("pop rsi");
    ropchain[5] = -8;
    ropchain[6] = __builtin_gadget_addr("sub rdi, rsi ; mov rdx, rdi");
    ropchain[7] = __builtin_gadget_addr("pop rax");
    ropchain[8] = ropchain+34;
    ropchain[9] = __builtin_gadget_addr("mov [rax], rdi");
    ropchain[10] = __builtin_gadget_addr("pop rsi");
    ropchain[11] = ropchain+36;
    ropchain[12] = __builtin_gadget_addr("mov rax, r8");
    ropchain[13] = __builtin_gadget_addr("mov [rsi], rax");
    ropchain[14] = __builtin_gadget_addr("pop rdi");
    ropchain[15] = *args++;
    ropchain[16] = __builtin_gadget_addr("pop rsi");
    ropchain[17] = *args++;
    ropchain[18] = __builtin_gadget_addr("pop rdx");
    ropchain[19] = *args++;
    ropchain[20] = __builtin_gadget_addr("pop rcx");
    ropchain[21] = *args++;
    ropchain[22] = __builtin_gadget_addr("pop r8");
    ropchain[23] = *args++;
    ropchain[24] = __builtin_gadget_addr("pop r9");
    ropchain[25] = *args++;
    ropchain[26] = __builtin_gadget_addr("xor rax, rax");
    ropchain[27] = fnaddr;
    ropchain[28] = __builtin_gadget_addr("pop rsi");
    ropchain[29] = ropchain+32;
    ropchain[30] = __builtin_gadget_addr("mov [rsi], rax");
    ropchain[31] = __builtin_gadget_addr("pop rcx");
    ropchain[32] = 0;
    ropchain[33] = __builtin_gadget_addr("pop rdi");
    ropchain[34] = 0;
    ropchain[35] = __builtin_gadget_addr("pop r8");
    ropchain[36] = 0;
    ropchain[37] = __builtin_gadget_addr("pop rsp");
    ropchain[38] = 0;
    return ((unsigned long long(*)(void))ropchain)();
}
