import sys, os

reg_map = {
    'A': 'rax',
    'B': 'rcx',
    'C': 'r10',
    'SP': 'rdi',
    'BP': 'r8'
}
conds = {'eq', 'ne', 'lt', 'le', 'gt', 'ge'}
# rsi is used as a scratch register for some operation
# r11 is used to back up a register when necessary

def make_label(_static_cntr=[0]):
    # all user-provided labels are underscore-prefixed
    ans = 'L%d'%_static_cntr[0]
    _static_cntr[0] += 1
    return ans

def warn(check_env, *msg):
    if check_env and check_env not in os.environ: return
    print('s2rop: warning:', *msg, file=sys.stderr)

def do_exchange_regs(mapping):
    if not mapping: return
    if list(mapping) == ['rax'] and ' ' not in mapping['rax']:
        print('mov rax,', mapping['rax'])
        return
    if 'rax' not in mapping: mapping['rax'] = 'rax'
    print('# do_exchange_regs:', mapping)
    items = list(mapping.items())
    labels_dst = {}
    for k, v in items:
        labels_dst[k] = make_label()
    for k, v in items:
        if v == 'rax':
            print('pop rsi')
            print('dp', labels_dst[k])
            print('mov [rsi], rax')
    cur_rax = 'rax'
    for k, v in items:
        if v != 'rax' and ' ' not in v and k != 'rax':
            cur_rax = v
            print('mov rax,', v)
            print('pop rsi')
            print('dp', labels_dst[k])
            print('mov [rsi], rax')
    if ' ' not in mapping['rax'] and mapping['rax'] != 'rax' and mapping['rax'] != cur_rax and 'r11' not in mapping:
        print('mov rax,', mapping['rax'])
    if 'r11' in mapping:
        print('pop r11 ; mov rax, rdi')
        print(labels_dst['r11']+':')
        if ' ' in mapping['r11']: print(mapping['r11'])
        else: print('dq 0')
    for k, v in items:
        assert ' ' not in k
        if (k != 'rax' or ' ' in v or v == 'rax' or 'r11' in mapping) and k not in ('rsp', 'r11'):
            print('pop', k)
            print(labels_dst[k]+':')
            if ' ' in v: print(v)
            else: print('dq 0')
    if 'rsp' in mapping:
        print('pop rsp')
        print(labels_dst['rsp']+':')
        if ' ' in mapping['rsp']: print(mapping['rsp'])
        else: print('dq 0')

cur_exchange={}
def exchange_regs(mapping): # {dst: src, ...}
    if mapping == None:
        do_exchange_regs(cur_exchange)
        cur_exchange.clear()
        return
    new_cur = {}
    for k in set(cur_exchange.keys()) | set(mapping.keys()):
        v = k
        v = mapping.get(v, v)
        v = cur_exchange.get(v, v)
        if v != k: new_cur[k] = v
    print('# exchange_regs', cur_exchange, '+', mapping, '=', new_cur)
    cur_exchange.clear()
    cur_exchange.update(new_cur)

def emit_instr(*args):
    assert not cur_exchange
    print(*args)

def emit_mov(reg_dst, reg_src):
    if reg_dst == 'rax' and not cur_exchange:
        if reg_src != 'rax':
            emit_instr('mov rax,', reg_src)
    else:
        if reg_src != 'rax':
            warn('CHECK_FALLBACK', 'mov %s, %s: fallback'%(reg_dst, reg_src))
        exchange_regs({reg_dst: reg_src})

def emit_binary_op(instr, reg_dst, reg_src, m1={}, m2={}):
    if reg_dst != 'rax' or reg_src != 'rcx':
        warn('CHECK_FALLBACK', '`%s` %s, %s: fallback'%(instr, reg_dst, reg_src))
    if reg_src == reg_dst:
        exchange_regs({reg_dst: 'rax', 'rax': reg_dst})
        exchange_regs({'r11': 'rcx', 'rcx': 'rax'})
        exchange_regs(m1)
        exchange_regs(None)
        emit_instr(instr)
        exchange_regs(m2)
        exchange_regs({'rcx': 'r11'})
        exchange_regs({'rax': reg_dst, reg_dst: 'rax'})
    elif reg_src == 'rax' and reg_dst == 'rcx':
        exchange_regs({'rax': 'rcx', 'rcx': 'rax'})
        exchange_regs(m1)
        exchange_regs(None)
        emit_instr(instr)
        exchange_regs(m2)
        exchange_regs({'rcx': 'rax', 'rax': 'rcx'})
    elif reg_src == 'rax':
        exchange_regs({'rax': 'rcx', 'rcx': 'rax'})
        exchange_regs({'rax': reg_dst, reg_dst: 'rax'})
        exchange_regs(m1)
        exchange_regs(None)
        emit_instr(instr)
        exchange_regs(m2)
        exchange_regs({reg_dst: 'rax', 'rax': reg_dst})
        exchange_regs({'rcx': 'rax', 'rax': 'rcx'})
    elif reg_dst == 'rcx':
        exchange_regs({'rax': 'rcx', 'rcx': 'rax'})
        exchange_regs({'rcx': reg_src, reg_src: 'rcx'})
        exchange_regs(m1)
        exchange_regs(None)
        emit_instr(instr)
        exchange_regs(m2)
        exchange_regs({reg_src: 'rcx', 'rcx': reg_src})
        exchange_regs({'rax': 'rcx', 'rcx': 'rax'})
    else:
        exchange_regs({'rax': reg_dst, reg_dst: 'rax'})
        exchange_regs({'rcx': reg_src, reg_src: 'rcx'})
        exchange_regs(m1)
        exchange_regs(None)
        emit_instr(instr)
        exchange_regs(m2)
        exchange_regs({reg_src: 'rcx', 'rcx': reg_src})
        exchange_regs({reg_dst: 'rax', 'rax': reg_dst})

def emit_unary_op(instr, reg):
    exchange_regs({'rax': reg, reg: 'rax'})
    exchange_regs(None)
    emit_instr(instr)
    exchange_regs({reg: 'rax', 'rax': reg})

def emit_load_imm(reg, imm):
    exchange_regs({reg: imm})

def emit_binary_op_imm(instr, reg, imm):
    if reg != 'rax':
        warn('CHECK_FALLBACK', '`%s` %s, `%s`: fallback'%(instr, reg, imm))
    exchange_regs({'rax': reg, reg: 'rax'})
    if instr == 'add rax, rcx':
        emit_load_imm('rsi', imm)
        exchange_regs(None)
        emit_instr('add rax, rsi')
    elif instr == 'sub rax, rcx ; sbb rdx, rcx' and imm.startswith('dq '):
        emit_load_imm('rsi', 'dq -('+imm[3:]+')')
        exchange_regs(None)
        emit_instr('add rax, rsi')
    else:
        exchange_regs({'r11': 'rcx'})
        emit_load_imm('rcx', imm)
        exchange_regs(None)
        emit_instr(instr)
        exchange_regs({'rcx': 'r11'})
    exchange_regs({reg: 'rax', 'rax': reg})

def emit_jump_imm(dst):
    if dst.startswith('.'):
        if dst in local_labels:
            dst = local_labels[dst]
        else:
            local_labels[dst] = make_label()
            dst = local_labels[dst]
    exchange_regs(None)
    emit_instr('pop rsp')
    emit_instr('dp', dst)

def emit_jump_reg(src):
    exchange_regs({'rsp': src})
    exchange_regs(None)

def emit_logic(opcode, a, b):
    if opcode == 'eq':
        emit_binary_op('cmp rax, rcx ; sete al\nmovzx eax, al', a, b)
    else:
        if opcode.endswith('t'): opcode = opcode[:-1]
        emit_binary_op('cmp rax, rcx ; sete al\nset%s al\nmovzx eax, al'%opcode, a, b)

def emit_logic_imm(opcode, a, imm):
    emit_load_imm('rsi', imm)
    exchange_regs({'rax': a, a: 'rax'})
    exchange_regs(None)
    emit_instr('cmp rax, rsi ; sete al')
    if opcode != 'eq':
        if opcode.endswith('t'): opcode = opcode[:-1]
        emit_instr('set%s al'%opcode)
    emit_instr('movzx eax, al')
    exchange_regs({a: 'rax', 'rax': a})

def emit_condjump(opcode, dst, a, b, imm=False):
    if dst.startswith('.'):
        if dst in local_labels:
            dst = local_labels[dst]
        else:
            local_labels[dst] = make_label()
            dst = local_labels[dst]
    if a == b:
        if 'e' in lbl and 'ne' not in lbl:
            emit_jump_imm(dst)
        return
    exchange_regs({'r11': a})
    if imm: emit_logic_imm(opcode, a, b)
    else: emit_logic(opcode, a, b)
    exchange_regs({'r11': a, a: 'r11'})
    exchange_regs({'rax': 'r11', 'r11': 'rax'})
    exchange_regs(None)
    l = make_label()
    emit_instr('shl rax, 3')
    emit_instr('pop rsi')
    emit_instr('dp %s+8'%l)
    emit_instr('add rax, rsi')
    emit_instr('mov rax, [rax]')
    emit_instr('pop rsi')
    emit_instr('dp %s'%l)
    emit_instr('mov [rsi], rax')
    emit_instr('mov rax, r11')
    emit_instr('pop rsp')
    emit_instr(l+':')
    emit_instr('dq 0') # target addr
    emit_instr('dp %s+24'%l) # continue as usual
    emit_instr('dp', dst) # branch

def format_imm(imm):
    if imm.startswith('.'):
        if imm not in local_labels: local_labels[imm] = make_label()
        imm = local_labels[imm]
    try: return 'dq '+hex(int(imm, 0))
    except ValueError: return 'dp '+imm

data_segments = []
data_partial_words = []
is_data = -1
local_labels = {}

def emit_nativecall(lbl):
    rdioff = [0]
    rsival = [None]
    def set_rdi(x):
        offset = rdioff[0] - x
        rdioff[0] = x
        if offset != rsival[0]:
            print('pop rsi')
            print('dq', offset)
            rsival[0] = offset
        print('sub rdi, rsi ; mov rdx, rdi')
    def load_rax():
        print('mov rax, [rdi]')
    def load_rax_const(s):
        print('pop rax')
        print(s)
    def load_rax_from(s):
        print('mov rax,', s)
    def store():
        print('mov [rdi], rax')
    def set_to_const(a, x):
        set_rdi(a)
        load_rax_const(x)
        store()
    def copy(a, b):
        set_rdi(b)
        load_rax()
        set_rdi(a)
        store()
    if lbl.startswith('.'):
        assert lbl.startswith('._native_')
        if lbl not in local_labels: local_labels[lbl] = make_label()
        print(local_labels[lbl]+':')
        lbl = lbl[9:]
    else:
        assert lbl.startswith('_')
        print(lbl+':')
        lbl = lbl[1:]
    if lbl == 'rop_call_funcptr':
        funcptr = True
        args_base = 16
    else:
        funcptr = False
        args_base = 8
    ropchain_base = -208
    # load arguments into registers
    set_to_const(ropchain_base, 'pop rdi')
    set_to_const(ropchain_base+16, 'pop rsi')
    set_to_const(ropchain_base+32, 'pop rdx')
    set_to_const(ropchain_base+48, 'pop rcx')
    set_to_const(ropchain_base+64, 'pop r8')
    set_to_const(ropchain_base+80, 'pop r9')
    set_to_const(ropchain_base+96, 'xor rax, rax') # number of floating-point varargs is always 0
    # call the function
    # will be overwritten later, need to take care of the alignment
    set_to_const(ropchain_base+104, 'nop')
    set_to_const(ropchain_base+112, 'nop')
    # mov rcx, rax
    set_to_const(ropchain_base+120, 'pop rsi')
    set_to_const(ropchain_base+136, 'mov [rsi], rax')
    set_to_const(ropchain_base+144, 'pop rcx')
    # restore SP and BP
    set_to_const(ropchain_base+160, 'pop rdi')
    set_to_const(ropchain_base+176, 'pop r8')
    # ret
    set_to_const(ropchain_base+192, 'pop rsp')
    copy(ropchain_base+200, 0)
    # args
    copy(ropchain_base+8, args_base)
    copy(ropchain_base+24, args_base+8)
    copy(ropchain_base+40, args_base+16)
    copy(ropchain_base+56, args_base+24)
    copy(ropchain_base+72, args_base+32)
    copy(ropchain_base+88, args_base+40)
    # take care of the alignment
    # will overwrite one of the nop slots
    set_rdi(ropchain_base+112)
    load_rax_from('rdi')
    print('pop rcx')
    print('dq -16')
    print('and rax, rcx')
    if funcptr:
        set_rdi(args_base-0x20)
        print('mov rcx, [rdi + 0x18] ; lea rax, [rax + rcx - 1]')
        print('sub rax, rcx ; sbb rdx, rcx')
        print('pop rsi')
        print('dq 1')
        print('add rax, rsi')
    else:
        print('pop rcx')
        print('$'+lbl+'_addr')
    print('mov [rax], rcx')
    # back up SP, BP, lr
    set_rdi(8)
    load_rax_from('rdi')
    set_rdi(ropchain_base+168)
    store()
    set_rdi(ropchain_base+184)
    load_rax_from('r8')
    store()
    set_rdi(ropchain_base+152)
    load_rax_from('rdi')
    set_rdi(ropchain_base+128)
    store()
    lbl2 = make_label()
    set_rdi(ropchain_base)
    load_rax_from('rdi')
    print('pop rsi')
    print('dp', lbl2)
    print('mov [rsi], rax')
    print('pop rsp')
    print(lbl2+':')
    print('dq 0')

while True:
    try: l0 = input()
    except EOFError: break
    l = ' '.join(l0.split('#', 1)[0].replace(',', ', ').split())
    if not l: continue
    if l == '.text':
        is_data = -1
    elif l == '.data' or l.startswith('.data '):
        is_data = 0 if l == '.data' else int(l[6:])
        while len(data_segments) <= is_data:
            data_segments.append([])
            data_partial_words.append(b'')
        data_partial_words[is_data] += bytes((-len(data_partial_words[is_data])) % 8)
    elif l.endswith(':'):
        lbl = l[:-1]
        if lbl.startswith('.'): # local label
            if lbl in local_labels: lbl = local_labels[lbl]
            else:
                local_labels[lbl] = make_label()
                lbl = local_labels[lbl]
        else: # global label
            assert lbl.startswith('_')
            local_labels = {k: v for k, v in local_labels.items() if k.startswith('.S')}
        if is_data >= 0:
            assert len(data_partial_words[is_data]) % 8 == 0
            if data_partial_words[is_data]:
                data_segments[is_data].append('db '+repr(list(data_partial_words[is_data]))[1:-1])
                data_partial_words[is_data] = b''
            data_segments[is_data].append(lbl+':')
        else:
            exchange_regs(None)
            emit_instr(lbl+':')
    elif any(l.startswith(i) for i in ('.file ', '.loc ')):
        pass
    elif l.startswith('.string '):
        assert is_data >= 0
        arg = l0[l0.find('.string')+7:].strip()
        s = eval('b'+arg)+b'\0'
        s += bytes((-len(s)) % 8)
        data_partial_words[is_data] += s
    elif l.startswith('.byte '):
        assert is_data >= 0
        data_partial_words[is_data] += bytes((int(l[6:]) & 255,))
    elif l.startswith('.short '):
        assert is_data >= 0
        data_partial_words[is_data] += (int(l[7:]) & 65535).to_bytes(2, 'little')
    elif l.startswith('.int '):
        assert is_data >= 0
        data_partial_words[is_data] += (int(l[5:]) & 0xffffffff).to_bytes(4, 'little')
    elif l.startswith('.long '):
        assert is_data >= 0
        data_partial_words[is_data] += (int(l[6:]) & 0xffffffffffffffff).to_bytes(8, 'little')
    elif l.startswith('.ptr '):
        assert is_data >= 0
        assert len(data_partial_words[is_data]) % 8 == 0
        if data_partial_words[is_data]:
            data_segments[is_data].append('db '+repr(list(data_partial_words[is_data]))[1:-1])
        data_partial_words[is_data] = b''
        data_segments[is_data].append(format_imm(l[5:]))
    elif l.startswith('nativecall '):
        lbl = l[11:]
        emit_nativecall(lbl)
        continue
        lbl2 = make_label()
        lbl3 = make_label()
        print(lbl+':')
        print('pop rsi')
        print('dq 8')
        print('sub rdi, rsi ; mov rdx, rdi')
        print('pop rax')
        print('$'+lbl[1:]+'_addr')
        print('mov [rdi], rax')
        print('sub rdi, rsi ; mov rdx, rdi')
        print('pop rax')
        print('dp', lbl2)
        print('mov [rdi], rax')
        print('pop rsp')
        print('dp ___builtin_nativecall')
        print(lbl2+':')
        print('pop rsi')
        print('dq -8')
        print('sub rdi, rsi ; mov rdx, rdi')
        print('mov rax, [rdi]')
        print('sub rdi, rsi ; mov rdx, rdi')
        print('pop rsi')
        print('dp', lbl3)
        print('mov [rsi], rax')
        print('pop rsp')
        print(lbl3+':')
        print('dq 0')
    else:
        print('#', l)
        if ' ' in l:
            cmd, args = l.split(' ', 1)
            args = args.split(', ')
        if cmd == 'sub' and args[0] == 'SP' and args[1] not in reg_map:
            exchange_regs(None)
            emit_instr('pop rsi')
            emit_instr(format_imm(args[1]))
            emit_instr('sub rdi, rsi ; mov rdx, rdi')
        elif cmd == 'load64' and args[1] == 'SP':
            emit_binary_op('mov rax, [rdi]', reg_map[args[0]], 'rdi', {'rdi': 'rcx', 'rcx': 'rdi'}, {'rcx': 'rdi', 'rdi': 'rcx'})
        elif cmd == 'store64' and args[1] == 'SP':
            emit_binary_op('mov [rdi], rax', reg_map[args[0]], 'rdi', {'rdi': 'rcx', 'rcx': 'rdi'}, {'rcx': 'rdi', 'rdi': 'rcx'})
        elif cmd == 'mov':
            if args[1] in reg_map:
                emit_mov(reg_map[args[0]], reg_map[args[1]])
            else:
                emit_load_imm(reg_map[args[0]], format_imm(args[1]))
        elif cmd in ('add', 'sub', 'mul', 'and', 'or', 'xor'):
            if cmd == 'mul': cmd = 'imul'
            instr = cmd+' rax, rcx'
            if cmd == 'sub': instr += ' ; sbb rdx, rcx'
            if args[1] in reg_map:
                emit_binary_op(instr, reg_map[args[0]], reg_map[args[1]])
            else:
                emit_binary_op_imm(instr, reg_map[args[0]], format_imm(args[1]))
        elif cmd in ('shl', 'shr'):
            if args[1] in reg_map:
                emit_binary_op(cmd+' rax, cl', reg_map[args[0]], reg_map[args[1]])
            else:
                emit_binary_op_imm(cmd+' rax, cl', reg_map[args[0]], format_imm(args[1]))
        elif cmd == 'not':
            emit_binary_op_imm('xor rax, rcx', reg_map[args[0]], 'dq 0xffffffffffffffff')
        elif cmd == 'jmp':
            if args[0] in reg_map:
                emit_jump_reg(reg_map[args[0]])
            else:
                emit_jump_imm(args[0])
        elif cmd.startswith('crop'):
            if cmd == 'crop64': continue
            bits = int(cmd[4:])
            emit_binary_op_imm('shl rax, cl\nshr rax, cl', reg_map[args[0]], 'dq '+str(64-bits))
        elif cmd.startswith('icrop') or cmd.startswith('load'):
            if cmd.startswith('load'):
                if cmd == 'load8': reg = 'al'
                elif cmd == 'load16': reg = 'ax'
                elif cmd == 'load32': reg = 'eax'
                elif cmd == 'load64': reg = 'rax'
                emit_binary_op('mov %s, [rdi]'%reg, reg_map[args[0]], reg_map[args[1]], {'rdi': 'rcx', 'rcx': 'rdi'}, {'rcx': 'rdi', 'rdi': 'rcx'})
                cmd = 'icrop'+cmd[4:]
            if cmd == 'icrop64': continue
            elif cmd == 'icrop32':
                exchange_regs({'r11': 'rdi'})
                exchange_regs({'rdi': 'rax'})
                exchange_regs(None)
                emit_instr('movsxd rax, edi')
                exchange_regs({'rdi': 'r11'})
            else:
                bits = int(cmd[5:])
                reg = reg_map[args[0]]
                if reg == 'rcx':
                    exchange_regs({'rax': 'rcx', 'rcx': 'rax'})
                    reg = 'rax'
                exchange_regs({'r11': 'rcx'})
                emit_load_imm('rcx', 'dq '+str(32-bits))
                emit_unary_op('shl rax, cl', reg)
                exchange_regs({'rdi': reg, reg: 'rdi'})
                exchange_regs(None)
                emit_instr('sar edi, cl')
                exchange_regs({'rcx': 'r11'})
                exchange_regs({'r11': 'rax'})
                exchange_regs(None)
                emit_instr('movsxd rax, edi')
                exchange_regs({'rdi': 'rax'})
                exchange_regs({'rax': 'r11'})
                exchange_regs({reg: 'rdi', 'rdi': reg})
                if reg_map[args[0]] == 'rcx':
                    exchange_regs({'rax': 'rcx', 'rcx': 'rax'})
        elif cmd in ('idiv', 'imod'):
            post = '\nmov rax, rdx' if cmd == 'imod' else ''
            if args[1] in reg_map:
                emit_binary_op('cqo ; idiv rsi'+post, reg_map[args[0]], reg_map[args[1]], m1={'rsi': 'rcx', 'rcx': 'rsi'}, m2={'rcx': 'rsi', 'rsi': 'rcx'})
            else:
                emit_unary_op('pop rsi\n'+format_imm(args[1])+'\ncqo ; idiv rsi'+post, reg_map[args[0]])
        elif cmd in ('div', 'mod'):
            post = '\nmov rax, rdx' if cmd == 'mod' else '\nsub rax, rcx ; sbb rdx, rcx'
            if args[1] in reg_map:
                emit_binary_op('pop rdx\ndq 0\ndiv rsi ; add rax, rcx'+post, reg_map[args[0]], reg_map[args[1]], m1={'rsi': 'rcx', 'rcx': 'rsi'}, m2={'rcx': 'rsi', 'rsi': 'rcx'})
            else:
                emit_unary_op('pop rdx\ndq 0\npop rsi\n'+format_imm(args[1])+'\ndiv rsi ; add rax, rcx'+post, reg_map[args[0]])
        elif cmd.startswith('store'):
            if cmd == 'store8':
                emit_binary_op('mov [rax], cl', reg_map[args[1]], reg_map[args[0]])
            elif cmd == 'store16':
                emit_binary_op('mov [rdi], cx', reg_map[args[1]], reg_map[args[0]], m1={'rdi': 'rax', 'rax': 'rdi'}, m2={'rax': 'rdi', 'rdi': 'rax'})
            elif cmd == 'store32':
                emit_binary_op('mov [rax], ecx', reg_map[args[1]], reg_map[args[0]])
            elif cmd == 'store64':
                emit_binary_op('mov [rax], rcx', reg_map[args[1]], reg_map[args[0]])
        elif cmd in conds:
            if args[1] in reg_map:
                emit_logic(cmd, reg_map[args[0]], reg_map[args[1]])
            else:
                emit_logic_imm(cmd, reg_map[args[0]], format_imm(args[1]))
        elif cmd.startswith('j') and cmd[1:] in conds:
            if args[2] in reg_map:
                emit_condjump(cmd[1:], args[0], reg_map[args[1]], reg_map[args[2]])
            else:
                emit_condjump(cmd[1:], args[0], reg_map[args[1]], format_imm(args[2]), imm=True)
        elif cmd == '.gadget_addr':
            emit_load_imm(reg_map[args[0]], ' '+', '.join(args[1:]))
        else:
            assert False, l
    #exchange_regs(None)

for i in range(len(data_segments)):
    for j in data_segments[i]:
        print(j)
    b = data_partial_words[i]
    b += bytes((-len(b)) % 8)
    if b:
        print('db '+repr(list(b))[1:-1])
