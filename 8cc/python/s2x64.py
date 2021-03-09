import sys

print('use64')

reg_map = {
    'A': 'rax',
    'B': 'rcx',
    'C': 'rdx',
    'SP': 'rsp',
    'BP': 'rbp'
}

conds = {
    'eq': 'e',
    'ne': 'ne',
    'lt': 'l',
    'gt': 'g',
    'le': 'le',
    'ge': 'ge'
}

while True:
    try: l0 = input()
    except EOFError: break
    l = ' '.join(l0.split('#', 1)[0].replace(',', ', ').split())
    if not l: continue
    if l == '.text':
        print('section .text')
    elif l == '.data' or l.startswith('.data '):
        depth = 0 if l == '.data' else int(l[6:])
        print('section .data.'+str(depth))
        print('align 8')
    elif l.endswith(':'):
        if l.startswith('_'):
            print('global', l[1:-1])
            print(l[1:])
            print('push r9')
            print('push r8')
            print('push rcx')
            print('push rdx')
            print('push rsi')
            print('push rdi')
            print('call', l[:-1])
            print('add rsp, 48')
            print('mov rax, rcx')
            print('ret')
        print(l)
    elif any(l.startswith(i) for i in ('.file ', '.loc ')):
        pass
    elif l.startswith('.string '): 
        arg = l0[l0.find('.string')+7:].strip()
        s = eval('b'+arg)+b'\0'
        print('db', repr(list(s))[1:-1])
    elif l.startswith('nativecall '): # cdecl-to-x64 wrapper for external calls
        name = l[11:]
        if name.startswith('._native'): name = name[8:]
        assert name[0] == '_', name
        print('extern', name[1:])
        print(l[11:]+':')
        print('mov rdi, [rsp+8]')
        print('mov rsi, [rsp+16]')
        print('mov rdx, [rsp+24]')
        print('mov rcx, [rsp+32]')
        print('mov r8, [rsp+40]')
        print('mov r9, [rsp+48]')
        print('xor al, al')
        print('call', name[1:])
        print('mov rcx, rax')
        print('ret')
    else:
        if ' ' in l:
            cmd, args = l.split(' ', 1)
            args = args.split(', ')
        else:
            cmd = l
            args = []
        if cmd in ('mov', 'add', 'sub', 'mul', 'and', 'or', 'xor'):
            if cmd == 'mul': cmd = 'imul'
            print('%s %s, %s'%(cmd, reg_map[args[0]], reg_map.get(args[1], args[1])))
        elif cmd == 'not':
            print('not', reg_map[args[0]])
        elif cmd == 'jmp':
            print('jmp', reg_map.get(args[0], args[0]))
        elif cmd in ('shl', 'shr', 'sar'):
            assert args[1] == 'B'
            print('%s %s, cl'%(cmd, reg_map[args[0]]))
        elif cmd.startswith('crop') or cmd.startswith('icrop'):
            if cmd in ('crop64', 'icrop64'): continue
            assert args[0] not in ('SP', 'BP')
            reg0 = reg_map[args[0]]
            reg = reg0
            sz = int(cmd.split('crop', 1)[1])
            asmcmd = 'movsx' if cmd.startswith('i') else 'movzx'
            if sz == 8:
                reg = reg[1]+'l'
            elif sz == 16:
                reg = reg[1:]
            elif sz == 32:
                reg = 'e'+reg[1:]
                if asmcmd == 'movsx': asmcmd = 'movsxd'
                else:
                    asmcmd = 'mov'
                    reg0 = reg
            print('%s %s, %s'%(asmcmd, reg0, reg))
        elif cmd in ('div', 'mod', 'idiv', 'imod'):
            print('push rax')
            print('push rax')
            print('push rdx')
            print('push rcx')
            if args[0] != 'A' or args[1] != 'B':
                print('push', reg_map[args[0]])
                print('push qword ', reg_map.get(args[1], args[1]))
                print('pop rcx')
                print('pop rax')
            if cmd.startswith('i'):
                print('cqo')
                print('idiv rcx')
            else:
                print('xor rdx, rdx')
                print('div rcx')
            print('mov [rsp+24],', 'rdx' if cmd == 'mod' else 'rax')
            print('pop rcx')
            print('pop rdx')
            print('pop rax')
            print('pop', reg_map[args[0]])
        elif cmd.startswith('store'):
            assert args[0] not in ('SP', 'BP') or cmd == 'store64'
            reg_src = reg_map[args[0]]
            if cmd == 'store32':
                reg_src = 'e'+reg_src[1:]
            elif cmd == 'store16':
                reg_src = reg_src[1:]
            elif cmd == 'store8':
                reg_src = reg_src[1]+'l'
            print('mov [%s], %s'%(reg_map[args[1]], reg_src))
        elif cmd.startswith('load'):
            reg_dst = reg_map[args[0]]
            xcmd = 'movsx'
            xsz = 'qword '
            if cmd == 'load32':
                xcmd = 'movsxd '
                xsz = 'dword '
            elif cmd == 'load16':
                xsz = 'word '
            elif cmd == 'load8':
                xsz = 'byte '
            else:
                xsz = ''
                xcmd = 'mov'
            print('%s %s, %s[%s]'%(xcmd, reg_map[args[0]], xsz, reg_map[args[1]]))
        elif cmd in conds:
            assert args[0] not in ('SP', 'BP')
            reg_dst = reg_map[args[0]]
            print('cmp %s, %s'%(reg_dst, reg_map.get(args[1], args[1])))
            print('set%s %sl'%(conds[cmd], reg_dst[1]))
            print('movzx %s, %sl'%(reg_dst, reg_dst[1]))
        elif cmd.startswith('j') and cmd[1:] in conds:
            print('cmp %s, %s'%(reg_map[args[1]], reg_map.get(args[2], args[2])))
            print('j%s %s'%(conds[cmd[1:]], args[0]))
        elif cmd in ('.byte', '.short', '.int', '.long', '.ptr'):
            print({'.byte': 'db', '.short': 'dw', '.int': 'dd', '.long': 'dq', '.ptr': 'dq'}[cmd], args[0])
        elif cmd == '.gadget_addr':
            assert args[1].startswith('dq '), args[1]
            print('mov %s, %s'%(reg_map[args[0]], args[1][3:]))
        else: assert False, l
