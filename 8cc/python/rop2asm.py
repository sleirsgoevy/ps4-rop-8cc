print('section .text')
print('use64')
print('global main')
print('main:')
print('mov rsp, rop_start')
print('ret')
print('extern exit')
print('section .data')
print('align 8')
print('rop_start:')

gid = 0

while True:
    try: l = input()
    except EOFError: break
    l = l.split('#', 1)[0].strip()
    if not l: continue
    if l == '$pivot_addr': l = 'mov rsp, [rdi+0x38] ; pop rdi'
    elif l == '$jop_frame_addr': l = 'push rbp ; mov rbp, rsp ; mov rax, [rdi] ; call [rax]'
    if l.startswith('$'):
        if l.endswith('_addr'):
            print('extern', l[1:-5])
            print('dq', l[1:-5])
        else:
            print(l[1:])
    elif l.endswith(':'):
        print('global '+l[:-1])
        print(l)
        print('section .text')
        print('global text_'+l[:-1])
        print('text_'+l)
        print('section .data')
    elif l.startswith('db ') or l.startswith('dq '):
        print(l)
    elif l.startswith('dp '):
        print('dq '+l[3:])
    else:
        print('dq gadget_'+str(gid))
        print('section .text')
        print('gadget_'+str(gid)+':')
        print(l.replace(' ; ', '\n'))
        print('ret')
        print('section .data')
        gid += 1
