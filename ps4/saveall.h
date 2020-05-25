#pragma once

typedef unsigned long long save_area_t[512]; // 1 page, just for sure

#define align_16(x) ((save_area_t*)((((unsigned long long)(x))+8)&~8))

void saveall(save_area_t* area);
void loadall(const save_area_t* area);

enum
{
    GP_REG_RAX = 0,
    GP_REG_RBX = 1,
    GP_REG_RCX = 2,
    GP_REG_RDX = 3,
    GP_REG_RSI = 4,
    GP_REG_RDI = 5,
    GP_REG_RBP = 6,
    GP_REG_RSP = 7,
    GP_REG_R8 = 8,
    GP_REG_R9 = 9,
    GP_REG_R10 = 10,
    GP_REG_R11 = 11,
    GP_REG_R12 = 12,
    GP_REG_R13 = 13,
    GP_REG_R14 = 14,
    GP_REG_R15 = 15,
    GP_REG_RIP = 16,
    // unknown values follow...
};
