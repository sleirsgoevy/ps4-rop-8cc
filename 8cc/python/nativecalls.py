lines = []

while True:
    try: s = input()
    except EOFError: break
    lines.append(s)

lines.append(':')

labels = {i[:-1] for i in (i.strip() for i in lines) if i.endswith(':') and not i.startswith('.')}
labels |= {'A', 'B', 'C', 'SP', 'BP'}

lines2 = []

j = 0
i = 0
while i < len(lines):
    l = lines[i].strip()
    if l.endswith(':') and not l.startswith('.'):
        ncalls = set()
        for ii in range(j, len(lines2)):
            ll = lines2[ii].strip()
            if ll.startswith('jmp ') and ll[4:] not in labels and ll[4] != '.':
                assert ll[4] == '_', ll
                ncalls.add(ll[5:])
                lines2[ii] = lines2[ii].replace(ll, 'jmp ._native_'+ll[5:])
        for x in ncalls:
            lines2.append('nativecall ._native_'+x)
        j = len(lines2)
    lines2.append(lines[i])
    i += 1

assert lines2[-1] == ':'
for i in lines2[:-1]:
    print(i)
