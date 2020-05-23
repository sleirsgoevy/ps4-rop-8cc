unsigned short __builtin_bswap16(unsigned short i)
{
    return (i<<8)|(i>>8);
}

unsigned int __builtin_bswap32(unsigned int i)
{
    return (i>>24)|((i&0x00ff0000u)>>8)|((i&0x0000ff00u)<<8)|(i<<24);
}

unsigned long long __builtin_bswap64(unsigned long long i)
{
    char* bytes = (char*)&i;
    for(int i = 0; i < 4; i++)
    {
        char c = bytes[7-i];
        bytes[7-i] = bytes[i];
        bytes[i] = c;
    }
    return i;
}
