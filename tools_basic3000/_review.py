# -*- coding: utf-8 -*-
"""Review union list: tails, suspicious words, junior-only leftovers."""
import json, io, sys
sys.stdout.reconfigure(encoding='utf-8')
BASE = r'D:\xuyuanfeng_qoder\tools_basic3000'
u = json.load(io.open(BASE + r'\_union.json', encoding='utf-8'))
print('total:', len(u))

def show(a, b):
    print('\n[%d..%d]' % (a, b))
    for i, e in enumerate(u[a:b], a + 1):
        print('%4d %-16s frq=%-6s bnc=%-6s %s' % (i, e['word'], e['frq'] or '-', e['bnc'] or '-', e['zh'][:36]))
    print('...')

show(3440, 3500)
show(3740, 3900)

print('\n== specific word checks ==')
known = {e['word'].lower(): e for e in u}
for w in ['russia', 'rusia', 'behaviour', 'behavior', 'behavious', 'hur', 'hurry', 'hurt', 'mm', 'pm', 'am', 'ad', 'dr', 'gy', 'organizer', 'organiser', 'receptionist', 'superman', 'hostess']:
    e = known.get(w)
    if e:
        print('%-12s FOUND  zh: %s' % (w, e['zh'][:60]))
    else:
        print('%-12s --' % w)

print('\n== junior-only words (%d) ==' % sum(1 for e in u if e['src'] == 'j'))
for e in u:
    if e['src'] == 'j':
        print(' ', e['word'], '|', e['zh'][:44])

import re
print('\n== suspicious patterns ==')
for e in u:
    w = e['word']
    if re.search(r'[^A-Za-z\'\- ]', w):
        print(' non-alnum:', repr(w), '|', e['zh'][:40])
    if w.isupper() and len(w) > 1:
        print(' all-caps:', repr(w), '|', e['zh'][:44])
    if w.lower() == w.upper() and any(c.isalpha() for c in w):
        pass
