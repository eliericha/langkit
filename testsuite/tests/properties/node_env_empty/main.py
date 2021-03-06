from __future__ import absolute_import, division, print_function

print('main.py: Running...')


import sys

import libfoolang


ctx = libfoolang.AnalysisContext()
u = ctx.get_from_buffer('main.txt', 'def a b c')
if u.diagnostics:
    for d in u.diagnostics:
        print(d)
    sys.exit(1)


def_node = u.root[0]
a_node = def_node.f_names[0]
print('def_node =', def_node)
print('a_node =', a_node)
print('def_node.p_lookup(a_node) =', def_node.p_lookup(a_node))

print('main.py: Done.')
